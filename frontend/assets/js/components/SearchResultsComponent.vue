<template>
  <div class="search">
    <!-- Search term -->

    <b-input-group class="mt-5 mb-5">
      
      <input class="form-control" v-model="searchTerm" placeholder="Type something">
      <b-input-group-append>
        <b-btn variant="primary" v-on:click="handleClicked">Search</b-btn>
      </b-input-group-append>

    </b-input-group>

    <!-- order/sort options -->
      <p href="#" target="_self">Number of results</p>
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
// import { search } from '../api';
import ListCustom from './ListCustom';

export default {
  name: 'SearchResultsComponent',

  components: {
    "list-custom": ListCustom,
  },

  props: {
    results: {},
  },

  data() {
    return {
      searchTerm: '',
      // results: [],
      prestineForm: true,
    };
  },

  methods: {
    handleClicked() {
      // let searchQuery = this.searchTerm ? `?search=${this.searchTerm}&` : '?';
      // this.prestineForm = false;
      
      // Object.keys(this.filterConfiguration).map(key => {
      //   const filter = this.filterConfiguration[key];

      //   if(Array.isArray(filter)) {
      //     for (let i = 0; i < filter.length; i++) {
      //       const element = filter[i];
      //       searchQuery += `${key}=${element.name}&`;
      //     }
      //   } else if (filter){
      //     searchQuery += `${key}=${filter.name}&`;
      //   }
      // });

      // search(searchQuery)
      //   .then((response) => {
      //     console.log(response);
      //     this.results = response.data.results;
      //   })
      //   .catch((error) => {
      //     console.log(error);
      //   });
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