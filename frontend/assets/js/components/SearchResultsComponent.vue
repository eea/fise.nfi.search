<template>
  <div class="search">
    <!-- Search term -->

    <b-input-group class="mt-5 mb-5 slinput">
      <i class="fa fa-search left-icon"></i>
      <input
        class="form-control" 
        v-model="searchTerm"
        v-on:keyup.enter="handleClicked"
        placeholder="Type something"
      >
        <b-input-group-append>
          <b-btn variant="primary"
            v-on:click="handleClicked"
          >Search</b-btn>
        </b-input-group-append>
        <i
          class="fa fa-close right-icon"
          v-on:click="removeSearchTerm"
        ></i>
    </b-input-group>

    <!-- result count -->
      <p href="#" target="_self">Number of results {{count}}</p>
      <hr>

    <!-- search results -->
    <list-custom
      v-if="myDataList.length > 0"
      :dataList="myDataList"
      v-on:selected-result="handleSelectedResult"
      v-b-modal.modal1
    ></list-custom>

    <div v-if="selectedResult">
      <!-- Modal Component -->
      <b-modal
        id="modal1"
        :title="selectedResult.title"
        size="lg"
        v-model="modalShow"
        ok-only
      >
        <p class="my-4">Country: {{selectedResult.country}}</p>
        <p class="my-4">Data set: {{selectedResult.data_set}}</p>
        <p class="my-4">Data type: {{selectedResult.data_type}}</p>
        <p class="my-4">Description: {{selectedResult.description}}</p>
        <p class="my-4">Info level: {{selectedResult.info_level}}</p>
        <p class="my-4">Resource type: {{selectedResult.resource_type}}</p>
        <p class="my-4">Topic category:  {{selectedResult.topic_category}}</p>
        <div v-if="selectedResult.download_url">
          <b-link :href="selectedResult.download_url">Download</b-link>
        </div>
        <div>
          NUTS levels:
          <b-badge
            v-for="nut in selectedResult.nuts_levels"
            variant="light"
            :key="nut"
          >{{nut}}</b-badge>
        </div>
        <div>
          Keywords:
          <b-badge
            v-for="keyword in selectedResult.keywords"
            variant="light"
            :key="keyword"
          >{{keyword}}</b-badge>
        </div>

      </b-modal>
    </div>

  </div>
</template>

<script>
import ListCustom from './ListCustom';


export default {
  name: 'SearchResultsComponent',

  components: {
    "list-custom": ListCustom,
  },

  props: {
    results: {},
    count: null,
  },

  data() {
    return {
      searchTerm: '',
      prestineForm: true,
      selectedResult: null,
      modalShow: false,
      myDataList: JSON.parse(JSON.stringify(this.results)),
    };
  },

  created() {
    console.log('this.myDataList', this.myDataList)
  },

  methods: {
    handleClicked() {
      setTimeout(() => {
        // will emit after the render updates the model
        this.$emit("updated-search-term", this.searchTerm);
      });
    },

    handleSelectedResult(ev) {
      this.selectedResult = ev;
      this.modalShow = true;
    },

    removeSearchTerm() {
      this.searchTerm = '';
      this.$emit("updated-search-term", this.searchTerm);
    },
  },

  watch: {
    results: function(val) {
      this.myDataList = JSON.parse(JSON.stringify(val));
    }
  }
};
</script>

<style scoped>
.nav-tabs .nav-link {
  border: 0;
}
.slinput {
  position: relative;
}
.slinput input {
  font-size: 1.6rem;
  padding-left: 4rem;
}
.slinput button {
  position: absolute;
  right: .5rem;
  top: 50%;
  transform: translateY(-50%);
  min-width: 120px;
  background-color:#666666;
  border-color: transparent;
  z-index: 4;
}
.slinput .fa-search {
  position: absolute;
  left: 1rem;
  z-index: 1;
  top: 50%;
  transform: translateY(-50%);
  font-size: 2rem;
  color:#666666;
  z-index: 4;
}
.slinput .fa-close {
  position: absolute;
  right: calc(1.2rem + 120px + 1rem);
  top:50%;
  transform:translateY(-50%);
  color:#666666;
  z-index: 4;
}
</style>
