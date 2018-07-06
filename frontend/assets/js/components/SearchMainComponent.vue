<template>
  <div class="container-fluid">
    <div class="row flex-xl-nowrap2">
      <div class="bd-sidebar col-md-4 col-xl-4 col-12">
        <searchFilters v-on:updated-filters="handleUpdatedFilter"></searchFilters>
      </div>
      <div class="pb-md-3 pl-md-5 bd-content col-md-8 col-xl-8 col-12"> 
        <div class="container">
          <div class="bd-content">
            <searchResults :filterConfiguration="filterConfiguration"></searchResults>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import SearchResultsComponent from "./SearchResultsComponent";
import SearchFiltersComponent from "./SearchFiltersComponent";

/**
 * TODO
 * + remove group and sort
 * + remove reaster/plot requests, show all sets
 * - update faces numbers and availability
 * - make searches on each facet
 * - insert debounce for requests
 * - implement design
 * - jsdocs
 */
export default {
  name: "SearchMainComponent",

  components: {
    searchResults: SearchResultsComponent,
    searchFilters: SearchFiltersComponent,
  },

  data() {
    return {
      filterConfiguration: {},
    };
  },

  methods: {
    handleUpdatedFilter(ev) {
      this.filterConfiguration = ev;
      this.obj = 3
    },
  },
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
h1,
h2 {
  font-weight: normal;
}
ul {
  list-style-type: none;
  padding: 0;
}
li {
  display: inline-block;
  margin: 0 10px;
}
a {
  color: #42b983;
}

.bd-sidebar {
  padding-left: 0;
  display: flex;
}

.bd-sidebar .jumbotron {
  margin-bottom: 0;
  min-height: 100vh;
  background-color: #e6e6e6;
}

</style>
