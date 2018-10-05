<template>
  <div>
    <div
      v-for="data in dataList"
      :key="data.id"
      class="d-flex align-items-start list-group-item-custom list-group-item-action">
        <a
          href="#"
          target="_self"
          class="flex-column align-items-start fise-search-list-link"
          v-on:click="handleClicked($event, data)"
        >
          <div class="result-wrapper">
            <img
              :title="data.resource_type"
              class="result-img"
              :src="getImageForResourceType(data.resource_type)"
              alt=""
            >
            <div class="result-content">
              <div class="result-header">
                <h5 class="mb-1"><sup v-if="data.document_type">[ {{data.resource_type}} ]</sup> {{data.title}}</h5>
              </div>
              <p
                class="mb-1 result-body"
              >
                {{truncate(data.description,200)}}...
              </p>
              <div class="result-information">
                <div class="result-information-item">
                  <span class="result-information-title">Topics: </span>
                  <span class="result-information-value">{{data.topic_category}}</span>
                </div>
                <div class="result-information-item">
                  <span class="result-information-title">Format: </span>
                  <span class="result-information-value">{{ data.resource_type }}</span>
                </div>
              </div>
            </div>
          </div>

        </a>
        <div v-if="data.download_url">
          <b-link
            class="btn btn-outline result-btn"
            :href="data.download_url"
            v-on:click="stopPropagation($event)"
          >
            <i class="fa fa-download"></i> Download
          </b-link>
        </div>
    </div>
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

    stopPropagation(ev) {
      ev.stopPropagation();
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
.black {
  color: #333;
}
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
  border: none;
}
.list-group-item-action {
  width: 100%;
  color: #333;
  text-align: inherit;
  padding-top: 1.5rem;
  padding-bottom: 1.5rem;
  &:hover, &:focus {
    background-color: #F4F4F4;
    .result-header {
      color: #118443;
    }
  }
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
.result-content {
  width: 100%;
}
.result-body {
  font-size: .9em;
}
.fise-search-list-link {
  color: #333;
  &:hover,
  &:focus {
    text-decoration: none;
    color: #333;
  }
}
.btn-outline {
  border: 2px solid var(--fise-dark-green);
  color: var(--fise-dark-green);
  border-radius: 0;

  .list-group-item-action:hover &,
  &:hover,
  &:focus {
    background-color: var(--fise-dark-green);
    color: #fff;
  }
}
.result-information {
  border-left: 3px solid #118443;
  padding-left: .8em;
  color: #666;
  margin-top: 1em;

  &-item {
    display: inline-block;
  }
  &-item + &-item {
    margin-left: 1em;
  }

  &-title {
    color: #999;
  }

  &-value {
    text-transform: capitalize;
  }
}

</style>
