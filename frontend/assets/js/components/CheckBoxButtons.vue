<template>
  <div>
    <a role="button" v-b-toggle="'collapse-' + componentName">
      <div class="filter-heading h5 d-flex align-items-center justify-content-between">
        {{title}}
        <span class="fa fa-angle-down"></span>
      </div>
      <div class="preview-text">{{listSummary}}</div>
    </a>
    <b-collapse :id="'collapse-' + componentName">
      <div role="group" class="filter-group">
        <label
          style="display:flex"
          v-for="dataItem in checkboxDataList"
          :key="componentName + dataItem.id"
        >
          <b-form-checkbox
            stacked
            :id="componentName + '' + dataItem.id"
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
import filters from '../mixins/filters';

const noOfResultsInSummary = 2;

export default {
  name: 'CheckBoxButtons',

  props: {
    checkboxDataList: {},
    componentName: '',
    title: '',
    clearAllFilters: false,
  },

  mixins: [filters],

  data() {
    return {
      mySelectedList: [],
    };
  },

  computed: {
    // will display a string with the first few element from the list
    listSummary: function makeListSummary() {
      return this.summary(this.checkboxDataList, noOfResultsInSummary);
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
    clearAllFilters: function() {
      this.mySelectedList = [];
    }
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
