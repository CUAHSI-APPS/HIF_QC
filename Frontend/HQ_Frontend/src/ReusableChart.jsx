'use strict';

import {VictoryChart,VictoryLine,VictoryScatter} from 'victory';

class ReusableChart extends React.Component {
  constructor(props){
    super(props);
  }

  render(){
    return(
      <VictoryChart>
        <VictoryScatter/>
      </VictoryChart>
    )
  }

}

export default ReusableChart;
