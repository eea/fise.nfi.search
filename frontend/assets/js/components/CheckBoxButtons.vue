<template>
  <div role="group" class="">
    <div>
      {{title}}
    </div>
    <label 
      style="display:flex"
      v-for="dataItem in dataList"
      :key="componentName + dataItem.id"
    >
      <b-form-checkbox
        stacked
        :id="componentName + dataItem.id"
        v-model="mySelectedList"
        :value="dataItem"
        v-on:change="handleClicked()"
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
    console.log(this.dataList);
    return {
      mySelectedList: []
    };
  },

  methods: {
    handleClicked() {
      setTimeout(() => {
        // will emit after the render updates the model
        console.log(this.mySelectedList)
        this.$emit("selected-" + this.componentName, this.mySelectedList);
      });
    }
  },
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
