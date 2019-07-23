'use strict';

import {VictoryChart,VictoryLine,VictoryTheme,VictoryZoomContainer} from 'victory';

class ReusableChart extends React.Component {
  constructor(props){
    super(props);
    this.colors = ["#c43a31","#c47631","#1F7077","#269834"]
  }

  render(){
    let charts = this.props.data.map((datastream, index) => {
      let color = index % 4;

      return(   <VictoryLine
          style={{
             data: { stroke: this.colors[color], strokeWidth: 1 },
             parent: { border: ".25px solid #ccc"}
           }}
          data={datastream}/>)
    })

    return(
      <VictoryChart scale={{x:"time"}}
          containerComponent={
              <VictoryZoomContainer downsample={100}/>
          }>
        {charts}
      </VictoryChart>
    )
  }

}

export default ReusableChart;
