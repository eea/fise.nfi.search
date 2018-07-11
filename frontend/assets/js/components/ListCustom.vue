<template>
  <div>
    <a
      v-for="data in dataList"
      :key="data.id"
      href="#"
      target="_self"
      class="list-group-item flex-column align-items-start list-group-item-action"
      v-on:click="handleClicked($event, data)"
    >
      <div class="d-flex w-100 justify-content-between">
        <h5 class="mb-1 blue">{{data.title}}</h5>
      </div>
      <p class="mb-1">
        {{data.description}}
      </p> 
      <small>{{data.topic_category}}</small>
    </a>
  </div>
</template>

<script>
export default {
  name: 'ListCustom',

  props: {
    dataList: {},
  },

  methods: {
    handleClicked(ev, data) {
      ev.preventDefault();
      setTimeout(() => {
        // will emit after the render updates the model
        this.$emit('selected-result', data);
      });
    },
  }
};
</script>

<style>
.align-items-start {
    -ms-flex-align: start !important;
    align-items: flex-start !important;
}
.flex-column {
    -ms-flex-direction: column !important;
    flex-direction: column !important;
}
.list-group-item {
    position: relative;
    display: block;
    padding: 0.75rem 1.25rem;
    margin-bottom: -1px;
    background-color: #fff;
    border: none;
}
.list-group-item-action {
    width: 100%;
    color: #333;
    text-align: inherit;
}
.blue {
  color: #005bff;
}
small {
  font-size: .9rem;
  color: #666;
}
</style>
