<template>
  <div class="container">
    <!-- Search term input -->
    <div class="row flex-xl-nowrap2 search-input-wrapper">
      <b-input-group class="slinput">
        <input
          class="form-control"
          placeholder="Search term"
          v-model="searchTerm"
          v-on:keyup.enter="handleClicked"
        >
          <b-input-group-append>
            <b-btn
              variant="primary"
              v-on:click="handleClicked"
            >Explore</b-btn>
          </b-input-group-append>
          <i
            class="fa fa-close right-icon"
            v-on:click="removeSearchTerm"
          ></i>
      </b-input-group>
    </div>

    <div class="row flex-xl-nowrap2 mt-5">
      <!-- facets section -->
      <div class="bd-sidebar col-md-4 col-xl-3 col-12 order-md-12">
        <search-filters
          v-on:updated-filters="handleUpdatedFilter"
          :updateSource="updateSource"
          :facets="facets"
        ></search-filters>
      </div>

      <!-- result section -->
      <div class="pb-md-3 bd-content col-md-8 col-xl-9 col-12 order-md-1"> 
        <div>
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
import { search, searchFullUrl } from '../api';


/**
 * TODO
 * - cache pages as long as searchQuery is same
 */
export default {
  name: 'SearchMainComponent',

  components: {
    'search-results': SearchResultsComponent,
    'search-filters': SearchFiltersComponent,
  },

  data() {
    return {
      searchTerm: '',
      facets: {},
      results: [],
      count: null,
      next: '',
      previous: '',
      searchQuery: '',
      updateSource: '',
      justStarted: true,
      searchTerm: '',
    };
  },

  methods: {
    handleClicked() {
      this.handleUpdatedSearchTerm(this.searchTerm);
    },

    removeSearchTerm() {
      this.searchTerm = '';
      this.handleUpdatedSearchTerm(this.searchTerm);
    },

    /**
     * this will issue the search but will only update the facets
     * it is called by the filter component (facets)
     */
    handleUpdatedFilter(searchQuery) {
      let resultSearchQuery = this.searchTerm ? `?search=${this.searchTerm}&` : '?';
      resultSearchQuery += searchQuery;
      this.searchQuery = searchQuery;

      search(resultSearchQuery)
        .then((response) => {
          if(this.justStarted) {
            this.facets = response.data.facets;
          } else {
            this.facets = response.data.facets;
            this.results = response.data.results;
            this.count = response.data.count;
            this.next = response.data.next;
            this.previous = response.data.previous;
          }
          this.updateSource = 'facet';
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
      let resultSearchQuery = val ? `?search=${val}&` : '?';
      resultSearchQuery += this.searchQuery;
      this.justStarted = false;

      search(resultSearchQuery)
        .then((response) => {
          if(this.searchTerm !== val) {
            this.facets = response.data.facets;     
          }
          this.updateSource = 'searchTerm'; 
          this.results = response.data.results;
          this.count = response.data.count;
          this.next = response.data.next;
          this.previous = response.data.previous;
          this.searchTerm = val;
        })
        .catch((error) => {
          console.log(error);
        });
    },

    /**
     * the server return the full url path for next and prev, we will use it as is
     */
    getPrevNextResults(prevNext) {
      const nextPrevUrl = this[prevNext];

      if(nextPrevUrl) {
        searchFullUrl(nextPrevUrl)
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
<style scoped lang="scss">
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
  height: 100%;
}

.bd-sidebar .jumbotron {
  margin-bottom: 0;
  background-color: #F7F7F7;
  border-radius: 0;
  border: 1px solid #D6D6D9;
}

.nav-tabs .nav-link {
  border: 0;
}

.search-input-wrapper {
  background-color: #078548;
  padding: 2rem 10rem;
  position: relative;
  z-index: 89;
}

.slinput {
  position: relative;
  border: 1px solid #fff;
  background-color: #fff;

  .input-group-append {
    margin-left: 0;
    order: 2;
  }

  input {
    padding-left: 2rem;
    box-shadow: none;
    border: none;
    border-radius: 0;
  }

  button {
    min-width: 150px;
    background-color:#8DC84C;
    color: #000;
    font-weight: bold;
    border-color: transparent;
    z-index: 4;
  }

  .fa-search {
    position: absolute;
    left: 1rem;
    z-index: 1;
    top: 50%;
    transform: translateY(-50%);
    font-size: 2rem;
    color:#666666;
    z-index: 4;
  }

  .fa-close {
    color:#666666;
    z-index: 4;
    order: 1;
    display: flex;
    align-items: center;
    padding: 0 1em;
  }
}

.result-content {
  width: 100%;
}

</style>

