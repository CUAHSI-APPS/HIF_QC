'use strict';

import {VictoryChart,VictoryLine,VictoryScatter} from 'victory';

class ReusableChart extends React.Component {
  constructor(props){
    super(props);
  }

  render(){
    return(
      <VictoryChart scale={{x:"time"}}>
        <VictoryLine data={this.props.data}/>
      </VictoryChart>
    )
  }

}

export default ReusableChart;
