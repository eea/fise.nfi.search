<template>
  <div role="group" class="">
    <div>
      {{title}}
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
      <span>{{dataItem.name}}</span>
      <span class="badge badge-primary">{{dataItem.number}}</span>
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
        console.log('selected-' + this.componentName)
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
     * @param {Object} val["corine land cover"] - example of a facet object
     * @param {number} val["corine land cover"].id
     * @param {string} val["corine land cover"].name
     * @param {number} val["corine land cover"].number - the new count
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
</style>
