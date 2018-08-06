<template>
  <div role="group" class="filter-group">
    <div>
      <h5>{{title}}</h5>
    </div>
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
        {{dataItem.name}}
        <span class="badge badge-primary">{{dataItem.number}}</span>
      </span>

    </label>
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

  methods: {
    handleClicked() {
      setTimeout(() => {
        // will emit after the render updates the model
        // console.log('selected-' + this.componentName)
        // console.log('this.mySelectedList', this.mySelectedList)
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
      // console.log('dataList updateFacetsCount val', val)
      // console.log('dataList this.myDataList', this.myDataList)
      // console.log('dataList this.dataList', this.dataList)
      for (const key in val) {
        if (val.hasOwnProperty(key)) {
          // console.log('dataList key', key)
          // console.log('dataList val[key]', val[key])

          const newFacetCount = val[key].number;
          this.myDataList[key] = Object.assign(this.myDataList[key], { number: newFacetCount });
          // console.log('dataList this.myDataList[key]', this.myDataList[key])

          if(this.mySelectedList[key]) {
            this.mySelectedList[key] = Object.assign(this.mySelectedList[key], { number: newFacetCount })
          }
        }
      }
    },
  }
};
</script>

<style scoped>
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
}

</style>
