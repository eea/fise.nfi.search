<template>
  <select 
    class="mb-3 form-control custom-select"
    v-model="selected"
    v-on:change="handleEmit"
  >
    <option value="">
      {{ message }}
    </option>
    <option 
      v-for="dataItem in myDataList" 
      v-bind:value="dataItem"
      :key="dataItem.id"
    >
      {{ dataItem.name }}
    </option>
  </select>
</template>

<script>
export default {
  name: "SelectCustom",

  props: {
    dataList: {},
    componentName: '',
    message: '',
  },

  data() {
    return {
      myDataList: JSON.parse(JSON.stringify(this.dataList)),
      selected: '',
    };
  },

  methods: {
    handleEmit() {
      setTimeout(() => { // will emit after the render updates the model
        this.$emit('selected-' + this.componentName, this.selected);
      })
    }
  }
};
</script>

<style>
</style>
