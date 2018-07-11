<template>
  <div class="search">
    <!-- Search term -->

    <b-input-group class="mt-5 mb-5">
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
    </b-input-group>

    <!-- result count -->
      <p href="#" target="_self">Number of results {{count}}</p>
      <hr>

    <!-- search results -->
    <list-custom 
      v-if="results.length > 0"
      :dataList="results"
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
      >
        <p class="my-4">Country: {{selectedResult.country}}</p>
        <p class="my-4">Data Set: {{selectedResult.data_set}}</p>
        <p class="my-4">Data Type: {{selectedResult.data_type}}</p>
        <p class="my-4">Description: {{selectedResult.description}}</p>
        <p class="my-4">Info Level: {{selectedResult.info_level}}</p>
        <p class="my-4">Resource Type: {{selectedResult.resource_type}}</p>
        <p class="my-4">Topic Category:  {{selectedResult.topic_category}}</p>
        <div v-if="selectedResult.download_url">
          <b-link :href="selectedResult.download_url">Download</b-link>
        </div>
        <div>
          Nuts levels:
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

    <div v-if="!prestineForm && results.length === 0">
      No results found
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
    };
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
  }
};
</script>

<style scoped>
.nav-tabs .nav-link {
  border: 0;
}
</style>