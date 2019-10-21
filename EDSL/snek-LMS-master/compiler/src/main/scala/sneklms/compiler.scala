package sneklms

import Base._
import java.io.{File, PrintWriter}
import lantern._
import Lisp._
import org.scala_lang.virtualized.virtualize
import org.scala_lang.virtualized.SourceContext
import scala.collection.mutable.ArrayBuffer
import scala.collection.mutable.ListBuffer
import scala.util.continuations
import scala.util.continuations._
import scala.virtualization.lms._
import scala.virtualization.lms.common._

// TODO (Fei Wang): the Serializable part is not working in LMS!!
trait CpsConv extends Serializable {
  implicit class Cps[T](simple: Iterable[T]) extends Serializable {

    def Cps() = new Cps(simple)

    def foreach[U](f: T => Unit @cps[U]) = {
      val iter = simple.iterator
      while(iter.hasNext){
        f(iter.next)
      }
    }

    def map[U, A](f: T => U @cps[A]) = {
      val builder = new ListBuffer[U]()
      val iter = simple.iterator
      while(iter.hasNext){
        builder += f(iter.next)
      }
      builder.result()
    }

    def foldLeft[U, A](init: U)(f: (U, T) => U @cps[A]) = {
      var temp = init
      val iter = simple.iterator
      while (iter.hasNext) {
        temp = f(temp, iter.next)
      }
      temp
    }
  }
}

trait Compiler extends ONNXLib with NNModule with UninlinedFunctionOps with CpsConv {
  implicit val pos = implicitly[SourceContext]

  // for value
  abstract class Value {
    def get = this
  }
  case class Literal[T](v: Rep[T]) extends Value
  case class Mut[T](v: Var[T]) extends Value
  case class Wrap(var v: Value) extends Value {
    override def get = v.get
  }
  case class Tens(v: TensorR) extends Value
  case class Ten(v: Tensor) extends Value
  case class Mods(v: Module) extends Value
  case class OPT(v: Optim) extends Value
  case class FloatCons(v: Float) extends Value
  case class ArrayV[T](v: ArrayBuffer[T]) extends Value
  case class ModelV(f: Model) extends Value
  case object VError extends Value
  import Dataset.DataLoader
  case class Dataset1(v: DataLoader) extends Value

  type Env = Map[String,Value]

  def compile[T,U](n: Any, m: Any)(op: (Rep[T], Rep[T]) => Rep[U])(implicit env: Env): Value = (compile(n), compile(m)) match {
    case (Literal(n: Rep[T]), Literal(m: Rep[T])) => Literal(op(n, m))
  }

  implicit def repToValue[T](x: Rep[T]) = Literal(x)
  val debug =true
  def printDebug(s: String) = if (debug) System.out.println(s)

  def printEnv(implicit env: Env) = {
    printDebug("====== Env =======")
    env foreach { case (k, v) => printDebug(s"$k -> $v") }
    printDebug("==================")
  }

  // def lantern_train(tree_data: Rep[Array[Array[Int]]], lossFun: Model, args: List[TensorR]) = {
  //   val startTime = get_time()
  //   val learning_rate = 0.05f
  //   val lr = learning_rate
  //   val hp = 1e-8f
  //   val loss_save = NewArray[Double](30)
  //   val addr = getMallocAddr() // remember current allocation pointer here
  //   val loopStart = get_time()
  //   val tree_number = tree_data.length / 4

  //   for (epoc <- (0 until 30): Rep[Range]) {
  //     var average_loss = 0.0f

  //     for (n <- (0 until tree_number): Rep[Range]) {
  //       val index    = n % tree_number
  //       val scores   = tree_data(index * 4)
  //       val words    = tree_data(index * 4 + 1)
  //       val leftchs  = tree_data(index * 4 + 2)
  //       val rightchs = tree_data(index * 4 + 3)
  //       val loss = lossFun match {
  //         case outerFun:F4Array => gradR_loss(outerFun.f(scores)(words)(leftchs)(rightchs))(Tensor.zeros(1))
  //       }
  //       //val loss = gradR_loss(lossFun(scores, words, leftchs, rightchs))(Tensor.zeros(1))
  //       val loss_value = loss.data(0)  // we suppose the loss is scalar (Tensor of size 1)
  //       average_loss = average_loss * (n) / (n+1) + loss_value / (n+1)

  //       val pars = ArrayBuffer(args : _*)
  //       val mems = ArrayBuffer((args map {x => Tensor.zeros_like(x.x)}) : _*)

  //       for ((par, mem) <- pars.zip(mems)) {
  //         par.clip_grad(5.0f)
  //         mem += par.d * par.d
  //         par.x -= par.d * lr / (mem + hp).sqrt()
  //         par.clear_grad()
  //       }

  //       resetMallocAddr(addr)  // reset malloc_addr to the value when we remember allocation pointer
  //     }

  //     loss_save(epoc) = average_loss
  //     val tempTime = get_time()
  //     printf("epoc %d, average_loss %f, time %lf\\n", epoc, average_loss, (tempTime - loopStart))

  //   }

  //   val loopEnd = get_time()
  //   val prepareTime = loopStart - startTime
  //   val loopTime = loopEnd - loopStart
  //   val timePerEpoc = loopTime / 30

  //   val fp2 = openf("results.txt", "w")
  //   fprintf(fp2, "unit: %s\\n", "1 epoch")
  //   for (i <- (0 until loss_save.length): Rep[Range]) {
  //     //printf("loss_saver is %lf \\n", loss_save(i))
  //     fprintf(fp2, "%lf\\n", loss_save(i))
  //   }
  //   fprintf(fp2, "run time: %lf %lf\\n", prepareTime, timePerEpoc)
  //   closef(fp2)
  // }

  @virtualize
  def compile(exp: Any)(implicit env: Env = Map.empty): Value = { printDebug(s"exp >> $exp"); exp } match {
    case "None" => unit(-1)
    case "new" => Mut(var_new(0))
    case "set"::(x: String)::a::Nil =>
      val Mut(vx: Var[Int]) = env(x)
      var_assign(vx, compile(a) match { case Literal(a: Rep[Int]) => a })
      unit(())
    case "set"::(x: String)::head::a::Nil =>
      val Mut(vx: Var[Int]) = env(x)
      val h: Rep[Int] = compile(head) match { case Literal(head: Rep[Int]) => head }
      val ad = compile(a) match {
        // case Literal(a: Rep[Int]) => a
        case FloatCons(a: Float) => a
      }
      var_assign(vx, h + ad)
      unit(())
    case "get"::(x: String)::Nil =>
      val Mut(vx: Var[Int]) = env(x)
      Literal(readVar(vx))
    case List("array-get", x40: String, i: Int) =>
      val Literal(arr: Rep[Array[Float]]) = compile(x40)
      Literal(arr(i))
    case List("getattr", x43: String, "data") =>
      val Tens(t: TensorR) = compile(x43)
      Literal(t.x.data)
    case "while"::t::body::Nil =>
      while (compile(t) match { case Literal(t: Rep[Boolean]) => t })
        compile(body) match { case Literal(b: Rep[Unit]) => b }
      unit(())
    case x: Int => unit(x)
    case x: String => {printDebug(s"search in env $x"); env(x)}
    case x: Float => FloatCons(x)
    case Str(x) => Literal(unit(x))
    case "*"::n::m::Nil =>
      compile[Int,Int](n, m)(_ * _)
    case "+"::n::m::Nil =>
      compile[Int,Int](n, m)(_ + _)
    case "-"::n::m::Nil =>
      compile[Int,Int](n, m)(_ - _)
    case List("/", n, m) =>
      compile[Float,Float](n, m)(_ / _)
    case List("/", x52, i: Int) =>
      compile(x52) match {
        case Literal(n: Rep[Int]) => Literal(n / i)
        case Literal(n: Rep[Float]) => Literal(n / i)
      }
    case List("%", x48, num: Int) =>
      val Literal(a: Rep[Int]) = compile(x48)
      Literal(a % num)
    case List("*", x31: String, base: Int, extra: Float) =>
      compile(x31) match {
        case Literal(n: Rep[Int]) => Literal(n * (base + extra))
        case Literal(n: Rep[Float]) => Literal(n * (base + extra))
      }
    case "=="::n::m::Nil =>
      compile[Int,Boolean](n, m)(_ == _)
    case "<"::n::m::Nil =>
      compile[Int,Boolean](n, m)(_ < _)
    case ">"::n::m::Nil =>
      compile[Int,Boolean](n, m)(_ > _)
    case "if"::c::t::e::Nil =>
      val Literal(rc: Rep[Boolean]) = compile(c)
      Literal(if (rc) compile(t) match { case Literal(t: Rep[Int]) => t } else compile(e) match { case Literal(e: Rep[Int]) => e })
    case "let"::(x: String)::a::b =>
      compile(b)(env + (x -> compile(a)))
    case "return"::x::Nil =>
      val Literal(rx: Rep[Any]) = compile(x)
      return rx
    case "print"::x::Nil =>
      val arg = compile(x) match { case Literal(x: Rep[String]) => x }
      printf("%s\\n", arg)
      unit(1)
    case "printf"::(Str(format)::args)::Nil =>
      Literal(printf(formatFromPython(format), args map (compile(_) match { case Literal(x) => x }) : _*))
    case "transform"::t => t match {
      case "toTensor"::Nil => Literal(())
      case "normalize"::t => Literal(()) // FIXME
      case "compose"::t => Literal(()) // FIXME
    }
    case "loader"::t::Nil => t match {
      case (dataset: String)::(train: String)::download::transformations =>
        // From the MNIST pytorch example
        val mean = 0.1307f
        val std = 0.3081f
        Dataset1(new DataLoader(dataset, train == "True", mean, std, Seq(1, 28, 28)))
    }
    case "for_dataloader"::(loader: String)::List(x11: String, t0: String, x12: String)::body::Nil =>
      val Dataset1(dataloader) = env(loader)
      val mem = getMallocAddr()
      dataloader.foreach { (idx: Rep[Int], data: Tensor, target: Rep[Int]) =>
        compile(body)(env + (x11 -> Literal(idx)) + (t0 -> Tens(TensorR(data))) + (x12 -> Literal(target)))
        resetMallocAddr(mem)
        ()
      }
      Literal(())
    case "call"::t =>
      t match {
        case List(x19, "step") =>
          val OPT(opt: Optim) = compile(x19)
          opt.step()
          Literal(())
        case List(x42, "backward") => Literal(())
        case "lossFun" :: (x25: String) :: (x26: String) ::Nil =>
          val nf = compile("lossFun").get
          val x25_ = compile(x25).get
          val x26_ = compile(x26).get
          printEnv
          printDebug(s"nf >> $nf")
          (nf, x25_, x26_) match {
            case ( ModelV(F1TensorR(f)), Tens(x1: TensorR), Tens(x2: TensorR) ) =>
              val loss = gradR_loss(x => f(x1)(x2))(Tensor.zeros(1))
              Literal(loss.data)
            case ( ModelV(F1TensorRArray(f)), Tens(x1: TensorR), Literal(x2: Rep[Array[Float]]) ) =>
              val loss = gradR_loss(x => f(x1)(x2))(Tensor.zeros(1))
              Literal(loss.data)
          }
        case x7::"zero_grad":: Nil =>
          val OPT(o: Optim) = compile(x7)
          o.zero_grad()
          Literal(())
        case "variable" :: ((st: String) :: (b: String) :: Nil) :: Nil => // TODO (Fei Wang): isInput is ignored
          compile(st)

        case "SGD" :: ((paras:List[String]) :: _ :: lr :: _ :: _ :: Nil) :: Nil =>
          val FloatCons(learning_rate) = compile(lr).asInstanceOf[FloatCons]
          val param: Seq[Module] = paras.map(x => compile(x).asInstanceOf[Mods].v).toSeq
          val module = new Module {
            val name = "dummy"
            val content: Seq[Module] = param
          }
          OPT(SGD(module, learning_rate))

        case "nn_linear"::(args: List[Int])::Nil =>
          Mods(Linear1D(args(1), args(0)))
        case "numpy"::"zeros"::x::Nil =>
          compile(x) match {
            case Literal(x: Rep[Int]) => NewArray[Int](x)
          }
        case "tensor_randinit"::(dim0:Int)::(dim1:Int)::(dummy:Int)::(scale:Float)::Nil =>
          Tens(TensorR(Tensor.randinit(dim0, dim1, scale)))
        case "tensor_zeros"::(dim0:Int)::Nil =>
          Tens(TensorR(Tensor.zeros(dim0)))
        case "tuple"::(args: List[String])::Nil => args match {
          case Nil => ArrayV(ArrayBuffer[TensorR]())
          case (x: String)::(y: String)::(z: String)::Nil =>
            val (Tens(xx), Tens(yy), Tens(zz)) = (compile(x), compile(y), compile(z))
            ArrayV(ArrayBuffer(xx, yy, zz))
          case _ => ???
        }
        // case "tensor"::(list: List[Int])::Nil => Tens(TensorR(Tensor.rand(list:_*)))
        case "tensor"::(args: List[Any])::Nil => args match {
          // case Nil => Tens(TensorR(Tensor()))
          case (y: Int)::Nil =>
            Tens(TensorR(Tensor.zeros(y)))
          case (x: Int)::(y: Int)::Nil =>
            Tens(TensorR(Tensor.zeros(x, y)))
          case (x: String)::(y: Int)::Nil =>
            val (Literal(array:Rep[Array[Float]])) = compile(x)
            Tens(TensorR(Tensor(array, y)))
        }
        case "lantern_read"::(filename: String)::Nil =>
          if (filename.endsWith(".words")) {
            val readSlot = NewArray[Int](1)
            val fp = openf(filename, "r")
            getInt(fp, readSlot, 0)
            val word_embedding_size = 300
            val word_embedding_length = readSlot(0)
            val word_embedding_data = NewArray[Array[Float]](word_embedding_length)

            for (i <- (0 until word_embedding_length): Rep[Range]) {
              word_embedding_data(i) = NewArray[Float](word_embedding_size)
              for (j <- (0 until word_embedding_size): Rep[Range]) {
                getFloat(fp, word_embedding_data(i), j)
              }
            }
            closef(fp)
            Literal(word_embedding_data)
          } else if (filename.endsWith(".tree")) {
            val readSlot = NewArray[Int](1) // need a new readingSlot, other wise have error
            val fp = openf(filename, "r")
            getInt(fp, readSlot, 0)
            val tree_number = readSlot(0)
            val tree_data = NewArray[Array[Int]](tree_number * 4) // each tree data has 4 lines (score, word, lch, rch)

            val readSlot1 = NewArray[Int](1) // yet another readingSlot, not sure if this one can be reused
            for (i <- (0 until tree_number): Rep[Range]) {
              getInt(fp, readSlot1, 0)
              for (j <- (0 until 4): Rep[Range]) {
                tree_data(i * 4 + j) = NewArray[Int](readSlot1(0))
                for (k <- (0 until readSlot1(0)): Rep[Range]) {
                  getInt(fp, tree_data(i * 4 + j), k)
                }
              }
            }
            closef(fp)
            Literal(tree_data)
          } else {
            ???
          }
        case "lantern_train"::(args: List[String])::Nil => args match {
          case (tree_data: String)::(lFun: String)::(tensors:List[String]) =>
            // lantern_train(env(tree_data) match { case x:Literal[Array[Array[Int]]] => x.v }, env(lFun) match { case x:ModelV => x.f }, (tensors map {env(_) match { case x:Tens => x.v }}))
            unit(())
        }
      }
    case "def"::(f: String)::(args: List[String])::(body: List[List[Any]])::r =>
      {System.out.println(s"adding $f"); f} match {
        case "lossFun" =>
          System.out.println("we're in lossfun area")
          val nenv = (env filter { case (_,v) => v.isInstanceOf[Tens]} map { case (k:String,v: Tens) => (k -> Base(v.v))}) ++
                     (env filter { case (_,m) => m.isInstanceOf[Mods]} map { case (k:String,v: Mods) => (k -> ModsR(v.v))})
          System.out.println("we made nenv")
          // printEnv(nenv)
          val model = compileModel("def"::f::args::body::Nil)(nenv)
          // System.out.println(s"We got model: $model")
          // model // how to return? can I somehow update env?
          compile(r)(env + (f -> ModelV(model)))
        case _ =>
          printDebug(s"body >> $body")
          printDebug(s"r    >> $r")
          val func = args match {
            case x1::Nil =>
              val fptr: Rep[String => Unit] = uninlinedFunc1 { (x1v: Rep[String]) =>
                compile(body)(env + (x1 -> Literal(x1v)) ) match {
                  // case Literal(n: Rep[Int]) => n
                  case _ => ()
                }
              }
              Literal(fptr)
            case x1::x2::Nil =>
              val fptr: Rep[(Int, Int) => Int] = uninlinedFunc2 { (x1v: Rep[Int], x2v: Rep[Int]) =>
                compile(body)(env + (x1 -> Literal(x1v)) + (x2 -> Literal(x2v)) ) match {
                  case Literal(n: Rep[Int]) => n
                }
              }
              Literal(fptr)
            case x1::x2::x3::x4::Nil =>
              val fptr: Rep[((Array[Float], Array[Float], Array[Float], Array[Float])) => Unit] = fun {
                (x1v: Rep[Array[Float]], x2v: Rep[Array[Float]], x3v: Rep[Array[Float]], x4v: Rep[Array[Float]]) =>
                  compile(body)(env + (x1 -> Literal(x2v)) + (x2 -> Literal(x2v)) + (x3 -> Literal(x3v)) + (x4 -> Literal(x4v)))
                  unit(())
              }
            Literal(fptr)
          }
          printDebug(s"******************$f")
          printDebug(s"******************$r")
          compile(r)(env + (f -> func))
      }
    case "len"::(x:String)::Nil =>
      val Dataset1(loader) = env(x)
      Literal(loader.length)
    case "lambda"::(f: String)::(x: String)::e::Nil =>
      lazy val fptr: Rep[Int => Int] = fun { (xv: Rep[Int]) =>
        compile(e)(env + (x -> Literal(xv)) + (f -> Literal(fptr))) match {
          case Literal(n: Rep[Int]) => n
        }
      }
      Literal(fptr)
    case "begin"::seq =>
      printDebug(s"seq >> $seq")
      val res = ((None: Option[Value]) /: seq) {
        case (agg, exp) => Some(compile(exp))
      }
      res.get
    case x::Nil =>
      compile(x)
    case f::(x: List[Any]) =>
      printDebug(s"f >> $f")
      printDebug(s"x >> $x")
      val args = x map(compile(_) match { case Literal(x: Rep[Int]) => x })
      printDebug(s"args >> $args")
      val nf = compile(f).get
      printEnv
      printDebug(s"nf >> $nf")
      (nf, args) match {
        case (Literal(f: Rep[Int => Int]), x1::Nil) => f(x1)
        case (Literal(f: Rep[((Int, Int)) => Int]), x1::x2::Nil) => f((x1, x2))
      }
    case Nil => // no main
      val x = unit(0)
      return x
  }

  // for valueR
  abstract class ValueR {
    def get = this
  }
  case class Base(v: TensorR) extends ValueR
  case class Func1[A](v: A => TensorR @diff) extends ValueR
  case class Func2[A, B](v: (A, B) => TensorR @diff) extends ValueR
  case class Func3[A, B, C](v: (A, B, C) => TensorR @diff) extends ValueR
  case class Cons[T](v: T) extends ValueR
  case class LitR[T](v: Rep[T]) extends ValueR
  case class MulR[T](v: Var[T]) extends ValueR
  case class WrapR(var v: ValueR) extends ValueR {
    override def get = v.get
  }
  case class Tup3(v1: TensorR, v2: TensorR, v3: TensorR) extends ValueR
  case class ABase(v: ArrayBuffer[TensorR]) extends ValueR
  case class AFunc1[A](v: A => ArrayBuffer[TensorR] @diff) extends ValueR
  case class AFunc2[A, B](v: (A, B) => ArrayBuffer[TensorR] @diff) extends ValueR
  implicit def getArrayBuffer(a: ValueR): ArrayBuffer[TensorR] = a match {
    case ABase(v) => v
  }
  case class ModsR(v: Module) extends ValueR

  abstract class Model
  case class Bare(f: TensorR => TensorR @diff) extends Model
  case class F1TensorRArray(f: TensorR => Rep[Array[Float]] => TensorR @diff) extends Model
  case class F1TensorR(f: TensorR => TensorR => TensorR @diff) extends Model
  case class F2TensorR(f: TensorR => TensorR => TensorR => TensorR @diff) extends Model
  case class F1Array(f: Rep[Array[Float]] => TensorR => TensorR @diff) extends Model
  case class F3Array(f: Rep[Array[Float]] => Rep[Array[Int]] => Rep[Array[Int]] => TensorR => TensorR @diff) extends Model
  case class F4Array(f: Rep[Array[Int]] => Rep[Array[Int]] => Rep[Array[Int]] => Rep[Array[Int]] => TensorR => TensorR @diff) extends Model

  def compileModel(exp: Any)(env: Map[String, ValueR]) = {

    val ("def":: (f:String) :: (args: List[String]) :: (body: List[List[Any]]) :: Nil) = exp
    // assert (args.size == 5, s"TODO: we only handle models with 5 inputs: 4 inputs for training data, 1 input for dummy Tensor, but args is $args")
    printDebug(s"main body >> $body")

    // now the body part should evaluates to TensorR @diff
    def com(exp: Any)(implicit envR: Map[String, ValueR] = Map.empty): ValueR @diff = exp match {

      case "def"::(f:String)::(args:List[String])::(body: List[Any])::r =>
        printDebug(s"def >> $f $args $body $r")
        args match {

          case "i"::(x2:String)::Nil => { // TODO: (Fei Wang) We assume that "i" means type Rep[Int], and assume that x2 is ArrayBuffer[TensorR] -- init
            val F = (i: Rep[Int], init: ArrayBuffer[TensorR]) => shift { (k: ArrayBuffer[TensorR] => Unit) =>
              lazy val func: Rep[Int] => (ArrayBuffer[TensorR] => Unit) => ArrayBuffer[TensorR] => Unit = FUNlm { (i: Rep[Int]) => (k: ArrayBuffer[TensorR] => Unit) => (x: ArrayBuffer[TensorR]) =>
                def sh_func: ((Rep[Int], ArrayBuffer[TensorR]) => ArrayBuffer[TensorR] @diff) = (i: Rep[Int], x: ArrayBuffer[TensorR]) => shift {k: (ArrayBuffer[TensorR] => Unit) => func(i)(k)(x)}
                RST(k(com(body)(envR + ("i" -> LitR(i), x2 -> ABase(init), f -> AFunc2(sh_func))) match {case ABase(a) => a} ))
              }
              func(i)(k)(init)
            }
            com(r)(envR + (f -> AFunc2(F)))
          }

          case x1::Nil => { // TODO: (Fei Wang) This function is wrong, because it is not yet recursive
            val F = { (x: TensorR) => shift { (k: TensorR => Unit) =>
              lazy val func = FUN0 { (k: TensorR => Unit) => (x: TensorR) =>
                // printDebug(s"in body >>> $body")
                RST{k(com(body)(envR + (x1 -> Base(x))) match {case Base(v) => v} )}
              }
              func(k)(x)
            }}
            printDebug(s"next >>> $r")
            com(r)(envR + (f -> Func1(F)))
          }
          case x1::x2::Nil => shift{(k: ValueR => Unit) => ???}
          case x1::x2::x3::Nil => { // TODO: (Fei Wang) this function is wrong, because the F and sh_func should have the same type
            // now we need to stage this function (maybe recursive)
            // TODO: (Fei Wang) Problem! type of F is determined by types of args!!
            val F = { (init: TensorR, lch: Rep[Array[Int]], rch: Rep[Array[Int]]) => shift { (k: TensorR => Unit) =>

              // stuff in here should return type Unit
              lazy val func: Rep[Int] => (TensorR => Unit) => TensorR => Unit = FUNl { (i: Rep[Int]) => (k: TensorR => Unit) => (x: TensorR) =>
                def sh_func = (i: Rep[Int]) => shift {k: (TensorR => Unit) => func(i)(k)(x)}
                // TODO: this could very much be wrong (Fei Wang)
                RST{k( com(body)(envR + (x1 -> Base(init), x2 -> LitR(lch), x3 -> LitR(rch))) match {case Base(v) => v} )}
              }
              func(0)(k)(init)
            }}
            printDebug(s"next >>> $r")
            com(r)(envR + (f -> Func3(F)))
          }
        }

      case "begin"::seq =>
        printDebug(s"seq >> $seq")
        seq match {
          case x :: Nil => com(x)
          case x :: y :: Nil => com(x); com(y)
          case x :: y :: z :: Nil => com(x); com(y); com(z)
          case _ => shift{(k: ValueR => Unit) => ???}
        }
        /*
        val res = seq.Cps.foldLeft(None: Option[ValueR]){
          //case (agg, "None") => agg
          case (agg, exp) => Some(com(exp))
        }
        res.get
        */

      case "let"::(x: String)::"new"::b =>
        com(b)(envR + (x -> ABase(ArrayBuffer[TensorR]())))
      case "let"::(x: String)::a::b =>
        com(b)(envR + (x -> com(a)))

      case "transform"::t => t match {
        case "toTensor"::Nil => LitR(())
        case "normalize"::t => LitR(()) // FIXME
        case "compose"::t => LitR(()) // FIXME
      }

      case "call"::t =>
        t match {
          case List("nll_loss", List(x45, x40, bool: String)) =>
            assert(bool == "True")
            val Base(t: TensorR) = com(x45)
            val LitR(x: Rep[Int]) = com(x40)
            val arr = NewArray[Int](1)
            arr(0) = x
            Base(t.nllLossB(arr))
          case List("log_softmax", List(x44, dimSet: String)) =>
            assert(dimSet == "dim=1")
            val Base(t: TensorR) = com(x44)
            Base(t.logSoftmaxB(1))
          case List("relu", List(x42)) =>
            val Base(t: TensorR) = com(x42)
            Base(t.relu())
          case List(x39, "view", a: Int, b: Int) =>
            val Base(t: TensorR) = com(x39)
            Base(t.resize(a, b))
          case List(x5 : String, List(x30 : String)) =>
            val Base(t: TensorR) = com(x30)
            val ModsR(v: Linear1D) = com(x5)
            Base(v(t))
            // (com(x5), com(x30)) match {
            //   case (ModsR(v: Linear1D), Base(t: TensorR)) => Base(v(t))
            // }
          case List(x28: String, "view", List(a: Int, b: Int)) =>
            val Base(x28_ : TensorR) = com(x28)
            Base(x28_.resize(a, b))
          case "tensor_randinit"::(dim0:Int)::(dim1:Int)::(dummy:Int)::(scale:Float)::Nil =>
            Base(TensorR(Tensor.randinit(dim0, dim1, scale)))
          case "tensor_zeros"::(dim0:Int)::Nil =>
            Base(TensorR(Tensor.zeros(dim0)))
          case "tuple"::(x:String)::(y:String)::(z:String)::Nil =>
            val (Base(xx: TensorR), Base(yy: TensorR), Base(zz: TensorR)) = (com(x), com(y), com(z))
            ABase(ArrayBuffer(xx, yy, zz))
          case "new_tuple"::Nil =>
            ABase(ArrayBuffer[TensorR]())
          case "tensor"::(x:String)::(y:Int)::Nil =>
            val LitR(array: Rep[Array[Float]]) = com(x)
            Base(TensorR(Tensor(array, y)))
          case "append"::(x:String)::(y:String)::Nil =>
            val ABase(xx: ArrayBuffer[TensorR]) = com(x)
            val Base(yy: TensorR) = com(y)
            xx.append(yy)
            Cons(())
          case (x:String)::"sigmoid"::Nil =>
            val Base(xx: TensorR) = com(x)
            Base(xx.sigmoid())
          case (x:String)::"tanh"::Nil =>
            val Base(xx: TensorR) = com(x)
            Base(xx.tanh())
          case (x:String)::"exp"::Nil =>
            val Base(xx: TensorR) = com(x)
            Base(xx.exp())
          case (x:String)::"sum"::Nil =>
            val Base(xx: TensorR) = com(x)
            Base(xx.sum())
          case (x:String)::"log"::Nil =>
            val Base(xx: TensorR) = com(x)
            Base(xx.log())
        }

      case "dot"::n::m::Nil =>
        printDebug(s"dot $n, $m")
        val Base(nn: TensorR) = com(n)
        val Base(mm: TensorR) = com(m)
        Base(nn dot mm)

      case "*"::n::m::Nil =>
        printDebug(s"* $n, $m")
        val Base(nn: TensorR) = com(n)
        val Base(mm: TensorR) = com(m)
        Base(nn * mm)
      case "+"::n::m::Nil =>
        printDebug(s"+ $n, $m")
        val Base(nn: TensorR) = com(n)
        val Base(mm: TensorR) = com(m)
        Base(nn + mm)
      case "-"::n::m::Nil =>
        printDebug(s"- $n, $m")
        val Base(nn: TensorR) = com(n)
        val Base(mm: TensorR) = com(m)
        Base(nn - mm)
      case "/"::n::m::Nil =>
        printDebug(s"/ $n, $m")
        val Base(nn: TensorR) = com(n)
        val Base(mm: TensorR) = com(m)
        Base(nn / mm)
      case "<"::n::m::Nil =>
        printDebug(s"< $n, $m")
        val vn: Rep[Int] = com(n) match {
          case LitR(nn: Rep[Int]) => nn
          case Cons(nn: Int) => nn
        }
        val vm: Rep[Int] = com(m) match {
          case LitR(mm: Rep[Int]) => mm
          case Cons(mm: Int) => mm
        }
        LitR(vn < vm)
      case ">="::n::m::Nil =>
        printDebug(s">= $n, $m")
        val vn: Rep[Int] = com(n) match {
          case LitR(nn: Rep[Int]) => nn
          case Cons(nn: Int) => nn
        }
        val vm: Rep[Int] = com(m) match {
          case LitR(mm: Rep[Int]) => mm
          case Cons(mm: Int) => mm
        }
        LitR(vn >= vm)

      case "array-set"::(array:String)::"data"::(index:String)::(value:Int)::Nil =>
        val Base(arr: TensorR) = com(array)
        val LitR(idx: Rep[Int]) = com(index)
        val Cons(vlu: Int) = com(value)
        arr.x.data(idx) = vlu
        Cons(())

      case "if"::c::t::e::Nil =>
        val LitR(rc: Rep[Boolean]) = com(c)
        // TODO: (Fei Wang): if t and e return TensorR type, we should use IF. If they return ArrayBuffer[TensorR] type, we should use IFm
        ABase(IFm(rc){com(t) match {case ABase(v) => v}}{com(e) match {case ABase(v) => v}})
      case "idx"::arr::idx::Nil =>
        com(arr) match {
          case ABase(array: ArrayBuffer[TensorR]) =>
            val Cons(i: Int) = com(idx)
            Base(array(i))
          case LitR(array: Rep[Array[Any]]) =>
            val LitR(i: Rep[Int]) = com(idx)
            LitR(array(i))
          // case LitR(array: Rep[Array[Array[Float]]]) =>
          //   val LitR(i: Rep[Int]) = com(idx)
          //   LitR(array(i))
        }

      case x: Int => Cons(x)
      case x: String =>
        printDebug(s"EnvR >> x > $x")
        envR(x)
      case x::Nil =>
        printDebug(s"single >> x > $x")
        com(x)

      case f::(x: List[Any]) =>
        printDebug(s"f >> $f")
        printDebug(s"x >> $x")
        val nf = com(f)
        printDebug(s"nf >> $nf")
        (nf, x) match {
          case (Func1(f: (TensorR => TensorR @diff)), a::Nil) =>
            com(a) match {
              case Base(aa: TensorR) => Base(f(aa))
            }
          // TODO: (Fei Wang) this case is shadowed by the case above !!!! Try other methods??
          case (Func1(f: (Rep[Int] => TensorR @diff)), a::Nil) =>
            com(a) match {
              case LitR(aa: Rep[Int]) => Base(f(aa))
              case Cons(aa: Int) => Base(f(aa))
            }
          case (AFunc2(f: ((Rep[Int], ArrayBuffer[TensorR]) => ArrayBuffer[TensorR] @diff)), a::b::Nil) =>
            printDebug(s"in function >> nf > $f, x > $x")
            val ABase(bb: ArrayBuffer[TensorR]) = com(b)
            com(a) match {
              case LitR(aa: Rep[Int]) =>
                printDebug(s"before application >> nf > $f, aa > $aa, bb > $bb")
                ABase(f(aa, bb))
              case Cons(aa: Int) =>
                printDebug(s"before application >> nf > $f, aa > $aa, bb > $bb")
                ABase(f(aa, bb))
            }
        }

      case todo => {printDebug(s"todo>>>$todo"); shift{(k: ValueR => Unit) => ???} }
    }

    // TODO: (Fei Wang): this is assuming the knowledge about the types of args
    if (args.size == 2) {
      // assume that it is the tensor mul tensor case
      F1TensorRArray {(base: TensorR) => (x : Rep[Array[Float]]) =>
        com(body)(env + (args(0) -> Base(base), args(1) -> LitR(x))) match {case Base(v) => v}
      }
      // F1TensorR {(base: TensorR) => (x: TensorR) =>
      //   com(body)(env + (args(0) -> Base(base), args(1) -> Base(x))) match {case Base(v) => v}
      // }
    } else if (args.size == 3) { // assume that it is the tensor mul tensor case with dummy input
      F2TensorR {(base: TensorR) => (base1: TensorR) => (x: TensorR) =>
        com(body)(env + (args(0) -> Base(base), args(1) -> Base(base1), args(2) -> Base(x))) match { case Base(v) => v}
      }
    } else { // assume that it is treeLSTM case
      F4Array{ scores: Rep[Array[Int]] => words: Rep[Array[Int]] => lchs: Rep[Array[Int]] => rchs: Rep[Array[Int]] => x: TensorR =>
        val envR = env + (args(0) -> LitR(scores), args(1) -> LitR(words), args(2) -> LitR(lchs), args(3) -> LitR(rchs), args(4) -> Base(x))
        com(body)(envR) match { case Base(v) => v }
      }
    }
  }

  // for valueT (deprecated)
  abstract class ValueT {
    def get = this
  }

  case class LiteralT[T](v: Rep[T]) extends ValueT
  case class MutT[T](v: Var[T]) extends ValueT
  import Dataset.DataLoader
  case class DatasetV(v: DataLoader) extends ValueT
  case class TensorV(v: Tensor) extends ValueT
  case class FuncT[T, U](v: T => U) extends ValueT
  case class FuncWithDimsT[T, U](v: T => U, dims: Seq[Int]) extends ValueT


  class Result[+T](v: () => T @diff) {
    var x: Int = -1
    def apply() = {
      v()
    }
  }

  case class DiffV[T](v: Result[T]) extends ValueT
  type EnvT = Map[String, ValueT]

  val variables = new ArrayBuffer[TensorR]()
  val names = new ArrayBuffer[String]()
  var lr: Float = 0.05f
  var momentum: Float = 0.0f

  def formatFromPython(s: String) = {
    s.replace("{}", "%d").replace("{:.0f}", "%.0f").replace("{:.6f}", "%.6f").replace("%)", "%%)") + "\\n" // TODO escape % better
  }

  // @virtualize
  // def compileT(exp: Any)(implicit env: EnvT = Map.empty): ValueT = { printDebug(s"exp >> $exp"); exp } match {
  //   case "def"::(f: String)::(args: List[String])::(body: List[List[Any]])::r =>
  //     val func = args match {
  //       case x1::Nil =>
  //         lazy val fptr: Rep[Int => Unit] = uninlinedFunc1 { (x1v: Rep[Int]) =>
  //           compileT(body)(env + (x1 -> LiteralT(x1v)) + (f -> LiteralT(fptr))) match {
  //             // case DiffV(a: Function0[Unit @diff]) => val r = reset { a() }; unit(r)
  //             case LiteralT(_: Rep[Unit]) => unit(())
  //             case a => System.out.println(s"$a"); ???
  //           }
  //         }
  //         LiteralT(fptr)
  //     }
  //     compileT(r)(env + (f -> func))
  //   case "begin"::seq =>
  //     val res = ((None: Option[ValueT]) /: seq) {
  //       case (agg, exp) => Some(compileT(exp))
  //     }
  //     res.get
  //   case "call"::(fun: String)::(args: List[Any])::Nil => fun match {
  //     case "nll_loss" => (compileT(args(0)), compileT(args(1))) match {
  //       case (DiffV(a: Result[TensorR]), LiteralT(target: Rep[Int])) => DiffV[TensorR](new Result(() => a().nllLoss(target)))
  //     }
  //     case "relu" => (compileT(args(0))) match {
  //       case DiffV(a: Result[TensorR]) => DiffV[TensorR](new Result(() => a().relu()))
  //     }
  //     case "log_softmax" => compileT(args(0)) match {
  //       case DiffV(a: Result[TensorR]) => DiffV[TensorR](new Result(() => a().logSoftmax()))
  //     }

  //   }
  //   case "call"::(x: Any)::(member: String)::t => member match {
  //     case "backward" => compileT(x) match {
  //       case DiffV(a: Result[TensorR]) => TensorV(gradR_loss(dummy => a())(Tensor.scalar(0.0f)))
  //       case x => System.out.println(s">> $x"); ???
  //     }
  //     case "print" => compileT(x) match {
  //       case TensorV(a) => a.print(); LiteralT(())
  //       case DiffV(a: Result[TensorR]) =>
  //         // LiteralT(reset { val r = a(); r.print(derivative=true) })
  //         DiffV[Unit](new Result(() => { val r = a(); r.print(derivative=true) }))
  //       case LiteralT(x: Rep[Float]) => LiteralT(printf("%.4f\\n", x))
  //     }
  //     case "zero_grad" =>
  //       // for (pars <- variables) {
  //       //   pars.clear_grad()
  //       // }
  //       LiteralT(())
  //     case "view"  => t match { case (args: List[Int])::Nil =>
  //       compileT(x) match {
  //         case DiffV(a: Result[TensorR]) => DiffV[TensorR](new Result(() => a().resize(args.last))) // TODO handle general case
  //       }
  //     }
  //     case "step" =>
  //       for ((weight, idx) <- variables.zipWithIndex) {
  //         weight.x.addMul(-lr, weight.d)
  //         // weight.clear_grad()
  //       }
  //       LiteralT(())
  //   }
  //   case "array-get"::x::"data"::idx::Nil => (compileT(x), compileT(idx)) match {
  //     case (DiffV(a: Result[TensorR]), LiteralT(idx: Rep[Int])) =>
  //       var r: Tensor = null
  //       reset { val tensor = a(); r = tensor.x }
  //       LiteralT(r.data(idx))
  //     case (TensorV(a), LiteralT(idx: Rep[Int])) =>
  //       LiteralT(a.data(idx))
  //   }
  //   case "tensor"::(list: List[Int])::Nil => TensorV(Tensor.rand(list:_*))
  //   case "+"::n::m::Nil =>
  //     (compileT(n), compileT(m)) match {
  //       case (LiteralT(a: Rep[Int]), LiteralT(b: Rep[Int])) => LiteralT(a + b)
  //       case (LiteralT(a: Rep[Float]), LiteralT(b: Rep[Float])) => LiteralT(a + b)
  //       case (TensorV(a), TensorV(b)) => TensorV(a + b)
  //       case (DiffV(a: Result[TensorR]), DiffV(b: Result[TensorR])) => DiffV[TensorR](new Result(() => a() + b()))
  //     }
  //   case "/"::n::m::Nil =>
  //     System.out.println(s"/ $n $m")
  //     (compileT(n), compileT(m)) match {
  //       case (LiteralT(a: Rep[Float]), LiteralT(b: Rep[Int])) => LiteralT(a / b)
  //     }
  //   case "*"::n::m::t =>
  //     (compileT(n), compileT(m)) match {
  //       case (LiteralT(a: Rep[Int]), LiteralT(b: Rep[Int])) => LiteralT[Int](a * b)
  //       case (LiteralT(a: Rep[Float]), LiteralT(b: Rep[Int])) => LiteralT(a * b)
  //     }
  //   case "%"::n::m::Nil =>
  //     (compileT(n), compileT(m)) match {
  //       case (LiteralT(a: Rep[Int]), LiteralT(b: Rep[Int])) => LiteralT(a % b)
  //     }
  //   case "=="::n::m::Nil =>
  //     (compileT(n), compileT(m)) match {
  //       case (LiteralT(a: Rep[Int]), LiteralT(b: Rep[Int])) => LiteralT(a == b)
  //     }
  //   case "<"::n::m::Nil =>
  //     (compileT(n), compileT(m)) match {
  //       case (LiteralT(a: Rep[Int]), LiteralT(b: Rep[Int])) => LiteralT(a < b)
  //     }
  //   case "dot"::n::m::Nil =>
  //     (compileT(n), compileT(m)) match {
  //       case (TensorV(a), TensorV(b)) => TensorV(a dot b)
  //       case (DiffV(a: Result[TensorR]), DiffV(b: Result[TensorR])) => DiffV[TensorR](new Result(() => a() dot b()))
  //     }
  //   case "if"::c::t::e::Nil =>
  //     val LiteralT(rc: Rep[Boolean]) = compileT(c)
  //     LiteralT(if (rc) compileT(t) match { case LiteralT(t: Rep[Unit]) => t } else compile(e) match { case Literal(e: Rep[Unit]) => e })
  //   case "let"::(x: String)::a::b::Nil =>
  //     compileT(b)(env + (x -> compileT(a)))
  //   case "None" | Nil => LiteralT(())
  //   case "variable"::tn::(vol: String)::Nil =>
  //     compileT(tn) match {
  //       case TensorV(t) => DiffV[TensorR](new Result(() => {
  //         val res = TensorR(t)
  //         if (vol != "True") {
  //           variables += res
  //         }
  //         res
  //       }))
  //       case LiteralT(x) => LiteralT(x) // FIXME
  //     }
  //   case "transform"::t => t match {
  //     case "toTensor"::Nil => LiteralT(())
  //     case "normalize"::t => LiteralT(()) // FIXME
  //     case "compose"::t => LiteralT(()) // FIXME
  //   }
  //   case "loader"::t::Nil => t match {
  //     case (dataset: String)::(train: String)::download::transformations =>
  //       // From the MNIST pytorch example
  //       val mean = 0.1307f
  //       val std = 0.3081f
  //       DatasetV(new DataLoader(dataset, train == "True", mean, std, Seq(1, 28, 28)))
  //   }
  //   case "SGD"::(_::(l: Float)::_::(m: Float)::Nil)::Nil =>
  //     lr = l
  //     momentum = m
  //     LiteralT(()) // FIXME
  //   case "new" => MutT(var_new(0.0f))
  //   case "set"::(x: String)::t => t match { // FIXME HACK!!!!!
  //     case _::a::Nil =>
  //       val MutT(vx: Var[Float]) = env(x)
  //       var_assign(vx, compileT(a) match { case LiteralT(a: Rep[Float]) => a })
  //       LiteralT(unit(()))
  //     case a::Nil =>
  //       val MutT(vx: Var[Int]) = env(x)
  //       var_assign(vx, compileT(a) match { case LiteralT(a: Rep[Int]) => a })
  //       LiteralT(unit(()))
  //   }
  //   case "get"::(x: String)::Nil =>
  //     val MutT(vx: Var[Float]) = env(x)
  //     LiteralT(readVar(vx))
  //   case "while"::t::body::Nil =>
  //     while (compileT(t) match { case LiteralT(t: Rep[Boolean]) => t })
  //       compileT(body) match { case LiteralT(b: Rep[Unit]) => b }
  //     LiteralT(unit(()))
  //   case "for_dataloader"::(loader: String)::List(x11: String, t0: String, x12: String)::body::Nil =>
  //     val DatasetV(dataloader) = env(loader)
  //     val mem = getMallocAddr()
  //     dataloader.foreach { (idx: Rep[Int], data: Tensor, target: Rep[Int]) =>
  //       compileT(body)(env + (x11 -> LiteralT(idx)) + (t0 -> TensorV(data)) + (x12 -> LiteralT(target)))
  //       resetMallocAddr(mem)
  //       ()
  //     }
  //     LiteralT(())
  //   case "getattr"::(x: String)::(member: String)::Nil =>
  //     (compileT(x), member) match {
  //       case (DatasetV(loader), "dataset") => TensorV(loader.dataset)
  //     }

  //   case "len"::x::Nil => compileT(x) match {
  //     case DatasetV(loader) => LiteralT(loader.length)
  //     case TensorV(tensor) => LiteralT(tensor.shape(0))
  //   }
  //   case "printf"::(Str(format)::args)::Nil =>
  //     LiteralT(printf(formatFromPython(format), args map (compileT(_) match { case LiteralT(x) => x }) : _*))
  //   case "print"::Str(s)::Nil =>
  //     LiteralT(printf(s + "\\n"))
  //   case "onnx_load"::(filename: String)::Nil => {
  //     val model = readONNX(filename)
  //     val rfunc = FuncWithDimsT[Tensor, Tensor](model.inference_func, model.x_dims)
  //     rfunc
  //   }
  //   case "lantern_train"::((model: String)::(filename:String)::Nil)::Nil => {
  //     ???
  //   }
  //   case "lantern_run"::((model: String)::(filename: String)::Nil)::Nil => {
  //     // TODO: (Fei Wang) not yet using file name as data
  //     val FuncWithDimsT(func: (Tensor => Tensor), dims: Seq[Int]) = env(model)
  //     val inp = Tensor(readOnnxData(filename), dims: _*) // Tensor.zeros(dims: _*)
  //     // val inp2 = Tensor.zeros(dims: _*)
  //     TensorV(func(inp))
  //   }
  //   case x: String => env(x)
  //   case x: Int => LiteralT(unit(x))
  //   case x: Float => LiteralT(unit[Float](x))
  // }
}

@virtualize
trait UninlinedFunctionOps { this: DslOps =>
  def uninlinedFunc0[B:Manifest](f: Function0[Rep[B]]): Rep[Unit=>B]
  def uninlinedFunc1[A:Manifest,B:Manifest](f: Rep[A]=>Rep[B])(implicit pos: SourceContext): Rep[A => B]
  def uninlinedFunc2[A1:Manifest,A2:Manifest,B:Manifest](f: Function2[Rep[A1],Rep[A2],Rep[B]]): Rep[(A1,A2)=>B]
  // implicit def funManifest2[A1:Manifest,A2:Manifest,B:Manifest]: Manifest[(A1,A2) => B]
  def uninlinedFunc3[A1:Manifest,A2:Manifest,A3:Manifest,B:Manifest](f: Function3[Rep[A1],Rep[A2],Rep[A3],Rep[B]]): Rep[(A1,A2,A3)=>B]
  // implicit def funManifest3[A1:Manifest,A2:Manifest,A3:Manifest,B:Manifest]: Manifest[(A1,A2,A3) => B]
}

@virtualize
trait UninlinedFunctionOpsExp extends UninlinedFunctionOps { this: DslExp =>

  case class UninlinedFunc0[B:Manifest](b: Block[B]) extends Def[Unit => B] {
    val mB = manifest[B]
  }
  case class UninlinedFunc1[A:Manifest,B:Manifest](s:Sym[A], b: Block[B]) extends Def[A => B] {
    val mA = manifest[A]
    val mB = manifest[B]
  }
  case class UninlinedFunc2[A1:Manifest,A2:Manifest,B:Manifest](s1:Sym[A1], s2:Sym[A2], b: Block[B]) extends Def[(A1,A2) => B] {
    val mA1 = manifest[A1]
    val mA2 = manifest[A2]
    val mB = manifest[B]
  }
  // implicit def funManifest2[A1:Manifest,A2:Manifest,B:Manifest]: Manifest[(A1,A2) => B] = {
  //   manifestManifest
  // }
  case class UninlinedFunc3[A1:Manifest,A2:Manifest,A3:Manifest,B:Manifest](s1:Sym[A1], s2:Sym[A2], s3:Sym[A3], b: Block[B]) extends Def[(A1,A2,A3) => B] {
    val mA1 = manifest[A1]
    val mA2 = manifest[A2]
    val mA3 = manifest[A3]
    val mB = manifest[B]
  }
  //implicit def funManifest3[A1:Manifest,A2:Manifest,A3:Manifest,B:Manifest]: Manifest[(A1,A2,A3) => B] = {
  //  manifestManifest
  //}
  // override def boolean_or(lhs: Exp[Boolean], rhs: Exp[Boolean])(implicit pos: SourceContext) : Exp[Boolean] = lhs match {
  //   case Const(false) => rhs
  //   case _ => super.boolean_or(lhs, rhs)
  // }
  // override def boolean_and(lhs: Exp[Boolean], rhs: Exp[Boolean])(implicit pos: SourceContext) : Exp[Boolean] = lhs match {
  //   case Const(true) => rhs
  //   case _ => super.boolean_and(lhs, rhs)
  // }

  //   case class GenerateComment(l: String) extends Def[Unit]
  //   def generate_comment(l: String) = reflectEffect(GenerateComment(l))
  //   case class Comment[A:Manifest](l: String, verbose: Boolean, b: Block[A]) extends Def[A]
  //   def comment[A:Manifest](l: String, verbose: Boolean)(b: => Rep[A]): Rep[A] = {
  //     val br = reifyEffects(b)
  //     val be = summarizeEffects(br)
  //     reflectEffect[A](Comment(l, verbose, br), be)
  //   }

  //   override def boundSyms(e: Any): List[Sym[Any]] = e match {
  //     case Comment(_, _, b) => effectSyms(b)
  //     case _ => super.boundSyms(e)
  //   }

  //   override def array_apply[T:Manifest](x: Exp[Array[T]], n: Exp[Int])(implicit pos: SourceContext): Exp[T] = (x,n) match {
  //     case (Def(StaticData(x:Array[T])), Const(n)) =>
  //       val y = x(n)
  //       if (y.isInstanceOf[Int]) unit(y) else staticData(y)
  //     case _ => super.array_apply(x,n)
  //   }

  //   // TODO: should this be in LMS?
  //   override def isPrimitiveManifeste[T](m: Manifest[T]) = (m == manifest[String]) || super.isPrimitiveManifeste(m)

  override def doApply[A:Manifest,B:Manifest](f: Exp[A => B], x: Exp[A])(implicit pos: SourceContext): Exp[B] = {
    val x1 = unbox(x)
    val x1_effects = x1 match {
      case UnboxedTuple(l) => l.foldLeft(Pure())((b,a)=>a match {
        case Def(Lambda(_, _, yy)) => b orElse summarizeEffects(yy)
        case _ => b
      })
        case _ => Pure()
    }
    f match {
      case Def(Lambda(_, _, y)) => reflectEffect(Apply(f, x1), summarizeEffects(y) andAlso x1_effects)
      case _ => reflectEffect(Apply(f, x1), Simple() andAlso x1_effects)
    }
  }

  // BEGINNING UNINLINED FUNCTIONS
  val functionList0 = new scala.collection.mutable.HashMap[Sym[Any],Block[Any]]()
  val functionList1 = new scala.collection.mutable.HashMap[Sym[Any],(Sym[Any],Block[Any])]()
  val functionList2 = new scala.collection.mutable.HashMap[Sym[Any],(Sym[Any],Sym[Any],Block[Any])]()
  val functionList3 = new scala.collection.mutable.HashMap[Sym[Any],(Sym[Any],Sym[Any],Sym[Any],Block[Any])]()
  def uninlinedFunc0[B:Manifest](f: Function0[Rep[B]]) = {
    val b = reifyEffects(f())
    uninlinedFunc0(b)
  }
  def uninlinedFunc0[B:Manifest](b: Block[B]) = {
    val l = reflectEffect(UninlinedFunc0(b), Pure())
    functionList0 += (l.asInstanceOf[Sym[Any]] -> b)
    l
  }

  val topfunTable = new scala.collection.mutable.HashMap[Any,Sym[Any]]()
  def uninlinedFunc1[A:Manifest,B:Manifest](f: Exp[A] => Exp[B])(implicit pos: SourceContext): Exp[A => B] = {
    val can = canonicalize(f)
    topfunTable.get(can) match {
      case Some(funSym) =>
        funSym.asInstanceOf[Exp[A=>B]]
      case _ =>
        val funSym = fresh[A=>B]
        topfunTable += can->funSym.asInstanceOf[Sym[Any]]
        val s = fresh[A]
        val b = reifyEffects(f(s))
        functionList1 += (funSym.asInstanceOf[Sym[Any]] -> (s,b))
        funSym
    }
  }
  def canonicalize1(f: Any) = {
    val s = new java.io.ByteArrayOutputStream()
    val o = new java.io.ObjectOutputStream(s)
    o.writeObject(f)
    s.toString()
  }

  def uninlinedFunc2[A1:Manifest,A2:Manifest,B:Manifest](f: (Rep[A1],Rep[A2])=>Rep[B]) = {
    val can = canonicalize1(f)
    topfunTable.get(can) match {
      case Some(funSym) =>
        funSym.asInstanceOf[Exp[(A1,A2)=>B]]
      case _ =>
        val funSym = fresh[(A1,A2)=>B]
        topfunTable += can->funSym.asInstanceOf[Sym[Any]]
        val s1 = fresh[A1]
        val s2 = fresh[A2]
        val b = reifyEffects(f(s1,s2))
        functionList2 += (funSym.asInstanceOf[Sym[Any]] -> (s1,s2,b))
        funSym
    }
  }
  def uninlinedFunc2[A1:Manifest,A2:Manifest,B:Manifest](s1: Sym[A1], s2: Sym[A2], b: Block[B]) = {
    // val l = reflectEffect(UninlinedFunc2(s1,s2,b), Pure())
    // functionList2 += (l.asInstanceOf[Sym[Any]] -> (s1,s2,b))
    // l
    ???
  }

  def uninlinedFunc3[A1:Manifest,A2:Manifest,A3:Manifest,B:Manifest](f: Function3[Rep[A1],Rep[A2],Rep[A3],Rep[B]]) = {
    // val s1 = fresh[A1]
    // val s2 = fresh[A2]
    // val s3 = fresh[A3]
    // val b = reifyEffects(f(s1,s2,s3))
    // uninlinedFunc3(s1,s2,s3,b)
    ???
  }
  def uninlinedFunc3[A1:Manifest,A2:Manifest,A3:Manifest,B:Manifest](s1: Sym[A1], s2: Sym[A2], s3: Sym[A3], b: Block[B]) = {
    // val l = reflectEffect(UninlinedFunc3(s1,s2,s3,b), Pure())
    // functionList3 += (l.asInstanceOf[Sym[Any]] -> (s1,s2,s3,b))
    // l
    ???
  }
  /*
  override def doLambdaDef[A:Manifest,B:Manifest](f: Exp[A] => Exp[B]) : Def[A => B] = {
    val x = unboxedFresh[A]
    val y = reifyEffects(f(x)) // unfold completely at the definition site.
    //???

    Lambda(f, x, y)
  }*/
}

@virtualize
abstract class SnekDslSnippet[A:Manifest,B:Manifest] extends DslOps {
  def snippet(x: Rep[A]): Rep[B]
}

@virtualize
abstract class SnekDslDriverC[A:Manifest,B:Manifest](ddir: String, mmoduleName: String) extends SnekDslSnippet[A,B] with DslExp with UninlinedFunctionOpsExp { q =>
  val codegen = new DslGenC {
    val IR: q.type = q

    var dir: String = ""
    var moduleName: String = ""

    override def emitSource[A:Manifest](args: List[Sym[_]], body: Block[A], functionName: String, out: PrintWriter) = {

      val sA = remap(manifest[A])

      withStream(out) {
        stream.println(raw"""
        |#include <algorithm>
        |#include <assert.h>
        |#include <cblas.h>
        |#include <err.h>
        |#include <errno.h>
        |#include <fcntl.h>
        |#include <functional>
        |#include <iostream>
        |#include <math.h>
        |#include <memory>
        |#include <numeric>
        |#include <random>
        |#include <stdint.h>
        |#include <stdio.h>
        |#include <stdlib.h>
        |#include <string.h>
        |#include <sys/mman.h>
        |#include <sys/stat.h>
        |#include <sys/time.h>
        |#include <sys/types.h>
        |#include <time.h>
        |#include <unistd.h>
        |#include "$moduleName.h"
        |using namespace std;
        |#ifndef MAP_FILE
        |#define MAP_FILE MAP_SHARED
        |#endif
        |
        |int fsize(int fd) {
        |  struct stat stat;
        |  int res = fstat(fd, &stat);
        |  return stat.st_size;
        |}
        |
        |int printll(char *s) {
        |  while (*s != '\n' && *s != ',' && *s != '\t') {
        |    putchar(*s++);
        |  }
        |  return 0;
        |}
        |
        |long hash(char *str0, int len) {
        |  unsigned char *str = (unsigned char *)str0;
        |  unsigned long hash = 5381;
        |  int c;
        |
        |  while ((c = *str++) && len--)
        |    hash = ((hash << 5) + hash) + c; /* hash * 33 + c */
        |
        |  return hash;
        |}
        |
        |long HEAP_SIZE_CPU = 1073741826; // 1048576; // 536870912; // 268435456; // 2097152; 1610612739; // 4294967304; //
        |void *mallocBase = calloc(HEAP_SIZE_CPU, 1);
        |void *mallocAddr = mallocBase;
        |void *waterMark = mallocBase;
        |void *myMalloc(size_t bytes) {
        |  void *res = mallocAddr;
        |  mallocAddr = (void *)((char *)mallocAddr + bytes);
        |  if ((long)mallocAddr >= (long)mallocBase + HEAP_SIZE_CPU)
        |    fprintf(stderr, "CPU memory breached limit of HEAP_SIZE_CPU\n");
        |  return res;
        |}
        |
        |long HEAP_SIZE = 4294967304; // this is for GPU
        |
        |int timeval_subtract(struct timeval *result, struct timeval *t2, struct timeval *t1) {
        |  long int diff = (t2->tv_usec + 1000000 * t2->tv_sec) - (t1->tv_usec + 1000000 * t1->tv_sec);
        |  result->tv_sec = diff / 1000000;
        |  result->tv_usec = diff % 1000000;
        |  return (diff < 0);
        |}
        |
        |$templateRawCode
        |
        |void x1(char *);
        |
        |std::random_device rd{};
        |std::mt19937 gen{rd()};
        |std::normal_distribution<> d{0, 0.01};
        |
        |int main(int argc, char *argv[]) {
        |  if (argc != 2) {
        |    printf("usage: query <filename>\n");
        |    return 0;
        |  }
        |  x1(argv[1]);
        |  return 0;
        |}
        |""".stripMargin)

        emitFunctions(dir, moduleName)

        stream.println(sA+" "+functionName+"("+args.map(a => remapWithRef(a.tp)+" "+quote(a)).mkString(", ")+") {")

        emitBlock(body)

        val y = getBlockResult(body)
        if (remap(y.tp) != "void")
          stream.println("return " + quote(y) + ";")

        stream.println("}")
        stream.println("/*******************************************/")
      }
      Nil
    }

    override def emitNode(sym: Sym[Any], rhs: Def[Any]) = rhs match {
      case afs@ArrayFromSeq(xs) => stream.println(remap(afs.m) + " " + quote(sym) + "[" + xs.length + "] = {" + (xs map quote mkString ",") + "}; // ;)")
      case _ => super.emitNode(sym,rhs)
    }
    def tmpremap[A](m: Manifest[A]): String = m.toString match {
      case "Int" => "int"
      case _ => remap(m)
    }
    def emitFunctions(dir: String, moduleName: String) = {
      // Output prototypes to resolve dependencies
      withStream(new PrintWriter(s"$dir/$moduleName.h")) {
        stream.println("#ifndef _code")
        stream.println("#define _code")
        functionList0.foreach(f=>stream.println(tmpremap(getBlockResult(f._2).tp) + " " + quote(f._1) + "();"))
        functionList1.foreach(f=>stream.println(tmpremap(getBlockResult(f._2._2).tp) + " " + quote(f._1) + "(" + tmpremap(f._2._1.tp) + " " + quote(f._2._1) + ");"))
        functionList2.foreach(f=>stream.println(tmpremap(getBlockResult(f._2._3).tp) + " " + quote(f._1) + "(" + tmpremap(f._2._1.tp) + " " + quote(f._2._1) + ", " + tmpremap(f._2._2.tp) + " " + quote(f._2._2) +");\n"))
        functionList3.foreach(f=>stream.println(remap(getBlockResult(f._2._4).tp) + " " + quote(f._1) + "(" + remap(f._2._1.tp) + " " + quote(f._2._1) + ", " + remap(f._2._2.tp) + " " + quote(f._2._2) + ", " + remap(f._2._3.tp) + " " + quote(f._2._3) + ");\n"))
        stream.println("#endif")
      }
      withStream(new PrintWriter(s"$dir/$moduleName.i")) {
        stream.println(s"%module $moduleName")
        stream.println("%{")
        stream.println(s"""#include "$moduleName.h"""")
        stream.println("  #include <stdlib.h>")
        stream.println("  #include <stdio.h>")
        stream.println("  #include <stdint.h>")
        stream.println("  #include <math.h>")
        stream.println("  #include <unistd.h>")
        stream.println("  #include <sys/types.h>")
        stream.println("  #include <sys/stat.h>")
        stream.println("  #include <fcntl.h>")
        stream.println("  #include <sys/mman.h>")
        stream.println("%}")
        stream.println(s"""%include "$moduleName.h"""")
      }

      // Output actual functions
      functionList0.foreach(func => {
        stream.println(tmpremap(getBlockResult(func._2).tp) + " " + quote(func._1) + "() {")
        emitBlock(func._2)
        stream.println("return " + quote(getBlockResult(func._2)) + ";")
        stream.println("}\n")
      })
      functionList1.foreach(func => {
        stream.print(tmpremap(getBlockResult(func._2._2).tp) + " " + quote(func._1) + "(")
        stream.print(tmpremap(func._2._1.tp) + " " + quote(func._2._1))
        stream.println(") {")
        emitBlock(func._2._2)
        stream.println("return " + quote(getBlockResult(func._2._2)) + ";")
        stream.println("}\n")
      })
      functionList2.foreach(func => {
        stream.print(tmpremap(getBlockResult(func._2._3).tp) + " " + quote(func._1) + "(")
        stream.print(tmpremap(func._2._1.tp) + " " + quote(func._2._1) + ", ")
        stream.print(tmpremap(func._2._2.tp) + " " + quote(func._2._2))
        stream.println(") {")
        emitBlock(func._2._3)
        stream.println("return " + quote(getBlockResult(func._2._3)) + ";")
        stream.println("}\n")
      })
      functionList3.foreach(func => {
        stream.print(tmpremap(getBlockResult(func._2._4).tp) + " " + quote(func._1) + "(")
        stream.print(tmpremap(func._2._1.tp) + " " + quote(func._2._1) + ", ")
        stream.print(tmpremap(func._2._2.tp) + " " + quote(func._2._2) + ", ")
        stream.print(tmpremap(func._2._3.tp) + " " + quote(func._2._3))
        stream.println(") {")
        emitBlock(func._2._4)
        stream.println("return " + quote(getBlockResult(func._2._4)) + ";")
        stream.println("}\n")
      })
      functionList0.clear
      functionList1.clear
      functionList2.clear
      functionList3.clear
    }
  }

  codegen.dir = ddir
  codegen.moduleName = mmoduleName

  def indent(str: String) = {
    val strLines = str.split("\n")
    val res = new StringBuilder
    var level: Int = 0
    for (line <- strLines) {
      if(line.contains("}")) level -= 1
      res ++= (("  " * level) + line + "\n")
    if(line.contains("{")) level += 1
    }
    res.toString
  }

  lazy val code: String = {
    val source = new java.io.StringWriter()
    codegen.emitSource(snippet, "entrypoint", new PrintWriter(source))

    indent(source.toString)
  }

  def gen = {
    val file = new PrintWriter(s"$ddir/$mmoduleName.cpp")
    file.println(code)
    file.flush
    file.close
    import scala.sys.process._
    System.out.println(s"======= Compile module $mmoduleName ============")
    try {
      (s"make MODULE_NAME=$mmoduleName -C $ddir":ProcessBuilder).lines.foreach(Console.println _)
      System.out.println(s"========================================")
      true
    } catch {
      case _ => false
    }
  }

  def eval[A](a:A): Unit = { // TBD: should read result of type B?
    val filename = "/home/fei/bitbucket/snek-LMS/compiler/gen/snippet.cpp"
    val out = new java.io.PrintWriter(filename)
    out.println(code)
    out.close
    //TODO: use precompile
    (new java.io.File("/tmp/snippet")).delete
    import scala.sys.process._
    (s"g++ -std=c++11 -O3 $filename -o /tmp/snippet":ProcessBuilder).lines.foreach(Console.println _)
    (s"/tmp/snippet $a":ProcessBuilder).lines.foreach(Console.println _)
  }

}