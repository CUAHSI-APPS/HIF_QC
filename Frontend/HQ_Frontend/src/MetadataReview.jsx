class MetadataReview extends React.Component {
  constructor(props){
    super(props);
    this.state = {
      currentColView: 0,
      subpage: <></>
    }
    this.reviewCols = sessionStorage.dataCols;

    this.loadReviewSubPage = this.loadReviewSubPage.bind(this);

    this.loadReviewSubPage(0);
  }

  loadReviewSubPage(colNumber){
    if(colNumber < 0){
      colNumber = 0;
    }
    else if(colNumber >= this.reviewCols.length){
      colNumber = this.reviewCols.length-1;
    }

    // do query for subpage and apply back to div
    $('#metadata-view').load('/view/flagReview')


  }

  render(){

    return(
      <div id="page">
        <div className="arrow-left">left</div>
        <FlagView />
        <div className="arrow-right">right</div>
      </div>
    )
  }

}





export default MetadataReview;
