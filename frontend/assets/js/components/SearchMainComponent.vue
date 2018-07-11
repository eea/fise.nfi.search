<template>
  <div class="container-fluid">
    <div class="row flex-xl-nowrap2">
      <!-- facets section -->
      <div class="bd-sidebar col-md-4 col-xl-4 col-12">
        <search-filters 
          v-on:updated-filters="handleUpdatedFilter"
          :facets="facets"
        ></search-filters>
      </div>

      <!-- result section -->
      <div class="pb-md-3 pl-md-5 bd-content col-md-8 col-xl-8 col-12"> 
        <div class="container">
          <div class="bd-content">

            <search-results 
              v-on:updated-search-term="handleUpdatedSearchTerm"
              :results="results"
              :count="count"
            ></search-results>

            <!-- prev/next page -->
            <div>
              <b-button-group>
                <b-button 
                  v-if="previous"
                  variant="primary"
                  v-on:click="getPrevNextResults('previous')"
                >Prev
                </b-button>
                <b-button 
                  v-if="next"
                  variant="primary"
                  v-on:click="getPrevNextResults('next')"
                >Next
                </b-button>
              </b-button-group>
              <br><br>
            </div>

          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import SearchResultsComponent from './SearchResultsComponent';
import SearchFiltersComponent from './SearchFiltersComponent';
import { search } from '../api';


/**
 * TODO
 * + implement next/prev page
 * - cache pages as long as searchQuery is same
 * - implement metadata modal
 * - add download button
 */
export default {
  name: 'SearchMainComponent',

  components: {
    'search-results': SearchResultsComponent,
    'search-filters': SearchFiltersComponent,
  },

  data() {
    return {
      filterConfiguration: {},
      searchTerm: '',
      facets: {},
      results: [],
      count: null,
      next: '',
      previous: '',
      searchQuery: '',
    };
  },

  methods: {
    /**
     * this will issue the search but will only update the facets
     * it is called by the filter component (facets)
     */
    handleUpdatedFilter(val) {
      this.filterConfiguration = val;

      this.searchToUpdateFacets()
        .then((response) => {
          this.facets = response.data.facets;
        })
        .catch((error) => {
          console.log(error);
        });
    },

    /**
     * this will issue the search and update both the facets and the results
     * it is called by the result component by pressing the search button
     */
    handleUpdatedSearchTerm(val) {
      this.searchTerm = val;

      this.searchToUpdateFacets()
        .then((response) => {
          this.results = response.data.results;
          this.count = response.data.count;
          this.facets = response.data.facets;
          this.next = response.data.next;
          this.previous = response.data.previous;
        })
        .catch((error) => {
          console.log(error);
        });
    },

    /**
     * this will make a search request to the api based on the combined properties of the facets and search term
     * @returns promise
     */
    searchToUpdateFacets() {
      let searchQuery = this.searchTerm ? `?search=${this.searchTerm}&` : '?';
      
      Object.keys(this.filterConfiguration).map(key => {
        const filter = this.filterConfiguration[key];

        if(Array.isArray(filter)) { // for all the checkboxes
          for (let i = 0; i < filter.length; i++) {
            const element = filter[i];
            searchQuery += `${key}=${element.name}&`;
          }
        } else if (filter) { // for the country, which can only be one, there for it's not array
          searchQuery += `${key}=${filter.name}&`;
        }
      });
      this.searchQuery = searchQuery;

      return search(searchQuery);
    },

    getPrevNextResults(prevNext) {
      const nextPrevUrl = this[prevNext];
      console.log('nextPrev', nextPrevUrl)
      if(nextPrevUrl) {
        const pageNumber = nextPrevUrl.split('&page=')[1]
        const nextPrevResultsQuery = pageNumber ? this.searchQuery + '&page=' + pageNumber : this.searchQuery;

        search(nextPrevResultsQuery)
          .then((response) => {
            this.results = response.data.results;
            this.next = response.data.next;
            this.previous = response.data.previous;
          })
          .catch((error) => {
            console.log(error);
          });        
      }
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
