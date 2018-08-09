<template>
  <div>
    <a
      v-for="data in dataList"
      :key="data.id"
      href="#"
      target="_self"
      class="list-group-item-custom flex-column align-items-start list-group-item-action"
      v-on:click="handleClicked($event, data)"
    >
    <div class="result-wrapper">
      <img
        class="result-img"
        :src="getImageForResourceType(data.resource_type)"
        alt=""
      >
      <div class="result-content">
        <div class="result-header">
          <h5 class="mb-1 blue">{{data.title}}</h5>
        </div>
        <p class="mb-1">
          {{truncate(data.description,200)}}...
        </p>
        <small class="badge badge-primary">{{data.topic_category}}</small>
        <div v-if="data.download_url">
          <b-link class="btn btn-primary result-btn" :href="data.download_url">Download</b-link>
        </div>
      </div>
    </div>

    </a>
  </div>
</template>

<script>
import documentation from '../assets/documentation.png';
import rasterdata from '../assets/rasterData.png';
import report from '../assets/report.png';
import tabulardata from '../assets/tabularData.png';

const resultFormatImages = {
  'documentation': documentation,
  'rasterdata': rasterdata,
  'report': report,
  'tabulardata': tabulardata
}
export default {
  name: 'ListCustom',

  props: {
    dataList: {},
  },

  methods: {
    handleClicked(ev, data) {
      ev.preventDefault();
      this.$emit('selected-result', data);
    },

    truncate(text,limit) {
      return text.substring(0,limit)
    },

    getImageForResourceType(resourceType) {
      const formattedResType = resourceType.toLowerCase().replace(/[^A-Z0-9]+/gi, '');
      return resultFormatImages[formattedResType];
    }
  }
};
</script>

<style lang="scss">
.align-items-start {
  -ms-flex-align: start !important;
  align-items: flex-start !important;
}
.flex-column {
  -ms-flex-direction: column !important;
  flex-direction: column !important;
}
.list-group-item-custom {
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
.result-header {
  display: flex;
  justify-content: flex-start;
  align-items: center;
}
.result-img {
  height: 100px;
  width: 100px;
  margin-left: -20px;
  margin-top: -18px;
}
.result-wrapper {
  display: flex;
  justify-content: flex-start;
  align-items: center;
}
.result-btn {
  float: right;
  transform: scale;
  margin-top: -2rem;
}
</style>
