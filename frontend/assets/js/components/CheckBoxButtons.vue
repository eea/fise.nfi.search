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

  created() {
    this.myDataList = JSON.parse(JSON.stringify(this.dataList));
  },

  data() {
    return {
      mySelectedList: [],
      myDataList: [],
    };
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
    dataList: function (val) {
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
