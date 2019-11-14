'use strict';

import {VictoryChart,VictoryLine,VictoryTheme,VictoryZoomContainer, VictoryLabel, VictoryTooltip} from 'victory';

class ReusableChart extends React.Component {
  constructor(props){
    super(props);
    this.colors = ["#c43a31","#b47631","#1F7077","#269834"]
  }


  render(){
    let charts = this.props.data.map((datastream, index) => {
      let color = index % 4;

      return(   <VictoryLine
          style={{
             data: { stroke: this.colors[color], strokeWidth: 1 },
             parent: { border: ".25px solid #ccc"}
           }}
           labelComponent={<VictoryTooltip/>}
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
