<template>
  <div class="d3 d3--line">
    <svg class="line-graph"></svg>
    <div v-if="dataset.labels">
      <range-slider
        :dataList="dataset.labels" 
        :componentName="'year-published'"
        :selected="mySelectedList"
        v-on:selected-year-published="handleSelectedYearPublished"
      ></range-slider>      
    </div>
</div>
</template>

<script>
import * as d3 from 'd3';
import RangeSlider from './RangeSlider';

export default {
  name: 'PublishedYearsComponent',

  components: {
    'range-slider': RangeSlider,
  },

  props: {
    dataList: {},
    componentName: '',
    title: '',
  },

  data() {
    return {
      mySelectedList: [],
      myDataList: JSON.parse(JSON.stringify(this.dataList)),
      dataset: {},
      xScale: null,
      yScale: null,
    };
  },

  created() {
    setTimeout(() => {
      this.makeGraph();
    });
  },

  methods: {
    makeGraph() {
      const graphContainer = d3.select('.d3--line');
      const svg = d3.select('svg');
      const margin = { top: 50, right: 50, bottom: 50, left: 50 };
      const duration = 500;
      let width, height, innerWidth, innerHeight;
      let xScale, yScale;

      this.dataset = formatDataAndLabels(this.myDataList);

      destroyGraph();
      getDimentions();
      getScaleDomains.call(this);
      getScaleRanges();
      renderGraph.call(this);

      d3.select(window).on('resize', resize.bind(this));

      /**
       * will create the graph and the brush
       */
      function renderGraph() {
        if (!this.dataset.data.length || !this.dataset.labels.length) {
          return false;
        }
        let self = this;
        const area = d3
          .area()
          .x((d, i) => xScale(this.dataset.labels[i]))
          .y0(innerHeight)
          .y1(d => yScale(d));

        const xAxis = d3
          .axisBottom(xScale)
          .tickFormat((d, i) => this.dataset.labels[i]);
        const yAxis = d3.axisLeft(yScale).ticks(4);

        svg.attr('width', width).attr('height', height);

        const inner = svg.selectAll('g.inner').data([null]);
        inner.exit().remove();

        const brush = d3
          .brushX()
          .extent([[0, 0], [innerWidth, innerHeight]])
          .on('end', function() {
            brushed.call(this, self);
          });
        const gBrush = inner
          .enter()
          .append('g')
          .attr('class', 'inner')
          .attr('transform', `translate(${margin.top}, ${margin.right})`)
          .call(brush);

        const pathArea = svg
          .selectAll('g.inner')
          .selectAll('.path-area1')
          .data([null]);
        pathArea.exit().remove();
        pathArea
          .enter()
          .append('path')
          .attr('class', 'path-area path-area1')
          .attr('d', () => area(createZeroDataArray(this.dataset.data)))
          .on('click', function handleClicked(params) {
            let x = d3.event.x;
            let y = d3.event.y;
          })
          .transition()
          .duration(duration)
          .ease(d3.easePoly.exponent(2))
          .attr('d', area(this.dataset.data));

        this.xScale = xScale;
        this.brush = brush;
        this.gBrush = gBrush;

        function brushed(self) {
          if (!d3.event.sourceEvent) return; // Only transition after input.
          if (!d3.event.selection) return; // Ignore empty selections.

          const selection = scaleBandInvert(xScale);

          d3
            .select(this)
            .transition()
            .call(d3.event.target.move, selection.map(xScale));

          self.mySelectedList = [];

          self.mySelectedList.push(selection[0]);
          self.mySelectedList.push(selection[1]);

          self.emitSelected();
        }

        function scaleBandInvert(scale) {
          var eachBand = xScale.step();
          var index0 = Math.round(d3.event.selection[0] / eachBand);
          var index1 = Math.round(d3.event.selection[1] / eachBand);
          return [xScale.domain()[index0], xScale.domain()[index1]];
        }
      }

      function destroyGraph() {
        svg.selectAll('*').remove();
      }

      function getDimentions() {
        width = graphContainer.node().clientWidth;
        height = 200;
        innerWidth = width - margin.left - margin.right;
        innerHeight = height - margin.top - margin.bottom;
      }

      function getScaleRanges() {
        xScale.range([0, innerWidth]).paddingInner(1);
        yScale.range([innerHeight, 0]).nice();
      }

      function getScaleDomains() {
        xScale = d3.scaleBand().domain(this.dataset.labels);
        yScale = d3
          .scaleLinear()
          .domain([0, d3.max([d3.max(this.dataset.data)])]);
      }

      function createZeroDataArray(arr) {
        return new Array(arr.length).fill(0);
      }

      function formatDataAndLabels(set) {
        let result = { data: [], labels: [], codes: [] };
        Object.keys(set).map(key => {
          const item = set[key];
          result.data.push(item.number);
          result.labels.push(item.name);
          result.codes.push(key);
        });
        return result;
      }

      function resize() {
        destroyGraph();
        getDimentions();
        getScaleRanges();
        renderGraph.call(this, this.dataset);
      }
    },

    /**
     * handler for slider selecting years
     * @param {Object[]} ev - array containing the two years
     */
    handleSelectedYearPublished(ev) {
      this.mySelectedList = [];
      this.mySelectedList.push(ev[0]);
      this.mySelectedList.push(ev[1]);

      this.updateBrush(ev);
      this.emitSelected();
    },

    /**
     * will update the position of the brush, or create make it show
     */
    updateBrush(ev) {
      if (ev.length === 2) {
        this.gBrush
          .transition()
          .duration(350)
          .call(this.brush.move, ev.map(this.xScale));
      }
    },

    emitSelected() {
      setTimeout(() => {
        // will emit after the render updates the model
        this.$emit('selected-' + this.componentName, this.mySelectedList);
      });
    }
  },

  watch: {
    /**
     * on each change of the list in prop, received from the parent
     * it will update the facets (checkboxes) with the new count
     * Object.assign is needed so that Vue know that the model has been updatet
     * I tried creating a clone and assigning it at the end but it doesn't work (it keeps the previuos value in mySelectedList and doesn't update it)
     * @param {Object} val - the object that contains the list to display as checkboxes
     * @param {Object} val["corine land cover"] - example of a facet object OR val["1"]
     * @param {number} val["corine land cover"].id OR val["1"].id
     * @param {string} val["corine land cover"].name OR val["1"].name
     * @param {number} val["corine land cover"].number - the new count OR val["1"].number
     */
    dataList: function updateFacetsCount(val) {
      for (const key in val) {
        if (val.hasOwnProperty(key)) {
          const newFacetCount = val[key].number;

          this.myDataList[key] = Object.assign(this.myDataList[key], {
            number: newFacetCount
          });

          if (this.mySelectedList[key]) {
            this.mySelectedList[key] = Object.assign(this.mySelectedList[key], {
              number: newFacetCount
            });
          }
        }
      }
      this.makeGraph();
    }
  }
};
</script>

<style lang="scss">
$color-line: black;
$color-path-line1: #0baadd;
$color-path-line2: #47cf73;

.d3 {
  box-shadow: 0 0 0 1px #eee;
  box-sizing: border-box;
}
path,
line {
  fill: none;
  shape-rendering: crispEdges;
  stroke: $color-line;
}
.path-line {
  shape-rendering: initial;
  &.path-line1 {
    stroke: $color-path-line1;
  }
  &.path-line2 {
    stroke: $color-path-line2;
  }
}
.path-area {
  stroke: none;
  &.path-area1 {
    fill: rgba(11, 170, 221, 0.7);
    stroke: rgba(11, 170, 221, 0.7);
  }
  &.path-area2 {
    fill: rgba(71, 207, 115, 0.55);
    stroke: rgba(71, 207, 115, 0.55);
  }
}
.tick {
  text {
    font-family: sans-serif;
    font-size: 10px;
    fill: #999;
  }
}
</style>
