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
    ></list-custom>

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
    };
  },

  methods: {
    handleClicked() {
      setTimeout(() => {
        // will emit after the render updates the model
        this.$emit("updated-search-term", this.searchTerm);
      });
    },
  }
};
</script>

<style scoped>
.nav-tabs .nav-link {
  border: 0;
}
</style>