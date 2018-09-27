<template>
  <div>
    <a role="button" v-b-toggle="'collapse-' + componentName">
      <div class="filter-heading h5 d-flex align-items-center justify-content-between">
        {{title}}
        <span class="fa fa-angle-down"></span>
      </div>
      <div class="preview-text">{{summary}}</div>
    </a>
    <b-collapse :id="'collapse-' + componentName">
      <div role="group" class="filter-group">
        <label
          style="display:flex"
          v-for="dataItem in myDataList"
          :key="componentName + dataItem.id"
        >
          <b-form-checkbox
            stacked
            :id="componentName + dataItem.id"
            v-model="mySelectedList"
            :value="dataItem"
            v-on:change="handleClicked()"
            lazy
          ></b-form-checkbox>
          <span class="filter-item-name">
            {{dataItem.displayName || dataItem.name}}
            <span class="badge badge-primary">{{dataItem.number}}</span>
          </span>

        </label>
      </div>

    </b-collapse>
  </div>
</template>

<script>
export default {
  name: 'CheckBoxButtons',

  props: {
    dataList: {},
    componentName: '',
    title: '',
  },

  data() {
    return {
      mySelectedList: [],
      myDataList: JSON.parse(JSON.stringify(this.dataList)),
    };
  },

  computed: {
    summary() {
      let result = '';
      const noOfResultsInSummary = 2;
      const myDataListItems = Object.keys(this.myDataList);
      const remainingNumberOfResults = myDataListItems.length - noOfResultsInSummary;

      myDataListItems.slice(0, noOfResultsInSummary).map((key) => {
        result += this.myDataList[key].name + ', ';
      });
      result += '.. + ' + remainingNumberOfResults + ' more';
      return result;
    }
  },

  methods: {
    handleClicked() {
      setTimeout(() => {
        // will emit after the render updates the model
        this.$emit('selected-' + this.componentName, this.mySelectedList);
      });
    }
  },

  watch: {
    /**
     * on each change of dataList from prop, received from the parent
     * it will update the facets (checkboxes) with the new count
     * Object.assign is needed so that Vue knows that the model has been updated
     * I tried creating a clone (JSON.parse(JSON.stringify(this.dataList))) and assigning it at the end,
     * but it doesn't work (it keeps the previuos value in mySelectedList and doesn't update it)
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
          this.myDataList[key] = Object.assign(this.myDataList[key], { number: newFacetCount });

          if(this.mySelectedList[key]) {
            this.mySelectedList[key] = Object.assign(this.mySelectedList[key], { number: newFacetCount })
          }
        }
      }
    },
  }
};
</script>

<style scoped lang="scss">
.btn-group {
  position: relative;
  display: -ms-inline-flexbox;
  display: inline-flex;
  vertical-align: middle;
  flex-wrap: wrap;
}
.custom-control-inline {
  margin-right: 0;
}
.filter-group .badge {
  background-color: transparent;
  color: #5c5c5c;
  position: absolute;
  left: 100%;
  top: 0;
}
.filter-group .filter-item-name {
  position: relative;
}
.filter-group > label {
  cursor: pointer;
  margin-bottom: 0;
}

.preview-text {
  min-height: 0;
  opacity: 0;
  transition: .2s;
  height: 0;
  color: #999;
  font-size: .8em;
  .collapsed & {
    display: block;
    min-height: 3em;
    opacity: 1;
  }
}


</style>
