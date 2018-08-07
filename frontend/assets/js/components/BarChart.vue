<template>
  <div class="d3 d3--line">
    <svg class="line-graph"></svg>
    <div v-if="dataset.labels">
      <range-slider
        :dataList="dataset.labels" 
        :componentName="'year-published'"
        v-on:selected-year-published="handleSelectedYearPublished"
      ></range-slider>      
    </div>
</div>
</template>

<script>
import * as d3 from "d3";
import RangeSlider from './RangeSlider';


export default {
  name: "BarChart",

  components: {
    'range-slider': RangeSlider,
  },

  props: {
    dataList: {},
    componentName: "",
    title: ""
  },

  data() {
    return {
      mySelectedList: [],
      myDataList: JSON.parse(JSON.stringify(this.dataList)),
      dataset: {},
    };
  },

  created() {
    setTimeout(() => {
      this.makeGraph();
    });
  },

  methods: {
    makeGraph() {
      const graphContainer = d3.select(".d3--line");
      const svg = d3.select("svg");
      const margin = { top: 50, right: 50, bottom: 50, left: 50 };
      const duration = 500;
      let width, height, innerWidth, innerHeight;
      let xScale, yScale;

      this.dataset = formatDataAndLabels(this.myDataList);

      destroyGraph();
      getDimentions();
      getScaleDomains.call(this);
      getScaleRanges();
      renderGraph(this.dataset);

      d3.select(window).on("resize", resize.bind(this));

      function renderGraph(dataset) {
        if (!dataset.data.length || !dataset.labels.length) {
          return false;
        }
        const area = d3
          .area()
          .x((d, i) => xScale(dataset.labels[i]))
          .y0(innerHeight)
          .y1(d => yScale(d));

        const xAxis = d3
          .axisBottom(xScale)
          .tickFormat((d, i) => dataset.labels[i]);

        const yAxis = d3.axisLeft(yScale).ticks(4);

        svg.attr("width", width).attr("height", height);

        const inner = svg.selectAll("g.inner").data([null]);
        inner.exit().remove();
        inner
          .enter()
          .append("g")
          .attr("class", "inner")
          .attr("transform", `translate(${margin.top}, ${margin.right})`);

        // const xa = svg
        //   .selectAll("g.inner")
        //   .selectAll("g.x.axis")
        //   .data([null]);
        // xa.exit().remove();
        // xa
        //   .enter()
        //   .append("g")
        //   .attr("class", "x axis")
        //   .attr("transform", `translate(0, ${innerHeight})`)
        //   .call(xAxis);

        // const ya = svg
        //   .selectAll("g.inner")
        //   .selectAll("g.y.axis")
        //   .data([null]);
        // ya.exit().remove();
        // ya
        //   .enter()
        //   .append("g")
        //   .attr("class", "y axis")
        //   .call(yAxis);

        const pathArea1 = svg
          .selectAll("g.inner")
          .selectAll(".path-area1")
          .data([null]);
        pathArea1.exit().remove();
        pathArea1
          .enter()
          .append("path")
          .attr("class", "path-area path-area1")
          .attr("d", () => area(createZeroDataArray(dataset.data)))
          .on("click", function handleClicked(params) {
            let x = d3.event.x;
            let y = d3.event.y;
          })
          .transition()
          .duration(duration)
          .ease(d3.easePoly.exponent(2))
          .attr("d", area(dataset.data));
      }

      function destroyGraph() {
        svg.selectAll("*").remove();
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
        yScale = d3.scaleLinear().domain([0, d3.max([d3.max(this.dataset.data)])]);
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
        renderGraph(this.dataset);
      }
    },

    handleClicked() {
    },

    handleSelectedYearPublished(ev) {
      this.mySelectedList = [];

      const firstElementCode = this.dataset.codes[ev[0]];
      const firstElement = this.myDataList[firstElementCode];
      const secondElementCode = this.dataset.codes[ev[1]];
      const secondElement = this.myDataList[secondElementCode];

      this.mySelectedList.push(firstElement);
      this.mySelectedList.push(secondElement);
      this.emitSelected();
    },

    emitSelected() {
      setTimeout(() => {
        // will emit after the render updates the model
        this.$emit("selected-" + this.componentName, this.mySelectedList);
      });
    },
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
