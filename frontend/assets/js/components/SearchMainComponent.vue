<template>
  <div class="container">

    <!-- Search term input -->
    <div class="row flex-xl-nowrap2 search-input-wrapper">
      <b-input-group class="slinput">
          <div id="keywords-multiselect">
            <!-- <multiselect
              v-model="selectedKeywords"
              :options="keywords"
              :multiple="true"
              track-by="name"
              :custom-label="customLabel"
              :taggable="true"
              @tag="addTag"
              tag-placeholder="Add this as new keyword"
              placeholder="Search or add a keyword"
            >
            </multiselect> -->
            <search
              :allKeywords="keywords"
              @madeKeywords="handleSearch"
            ></search>
          </div>
          <b-input-group-append>
            <b-btn
              variant="primary"
              v-on:click="handleClickedSearchTerm"
            >Go</b-btn>
          </b-input-group-append>
          <!-- <i
            class="fa fa-close right-icon"
            v-on:click="removeSearchTerm"
          ></i> -->
      </b-input-group>
    </div>

    <button id="sidebarTrigger" ref="sidebarTrigger" class="btn btn-default">Open Filters</button>

    <div class="row flex-xl-nowrap2 mt-3">

      <!-- facets section -->
      <div class="bd-sidebar col-md-4 col-xl-3 col-12 order-md-12">
        <search-filters
          v-on:updated-filters="handleUpdatedFilter"
          :facets="facets"
        ></search-filters>
      </div>

      <!-- result section -->
      <div class="pb-md-3 bd-content col-md-8 col-xl-9 col-12 order-md-1"> 
        <div>
          <div class="bd-content">

            <!-- result count -->
            <div 
              class="result-count"
              v-if="showResultsCount"
            >
              <div 
                href="#" 
                target="_self" 
              >{{ showingResults }}
              </div>
              
              <!-- select page size -->
              <b-input-group prepend="results per page">
                <b-form-select 
                  v-model="pageSize"
                  :options="resultPerPage"
                  class="mb-3"
                  size="sm"
                  @change="handlePageChange()"
                />
              </b-input-group>

            </div>
            <hr style="width: 15rem;">

            <!-- loading result spinner -->
            <div v-if="loadingResults" class="spinner">
              <div class="loader"></div>
            </div>

            <search-results
              :results="results"
              :count="count"
              :currentPage="currentPage"
              :pageSize="resultsPerPage"
            ></search-results>

            <!-- pagination -->
            <div v-if="results.length > 0">
              <b-pagination
                size="sm"
                :total-rows="count"
                v-model="currentPage"
                :per-page="resultsPerPage"
                align="center"
                @change="handlePageChange()"
              ></b-pagination>
            </div>

          </div>
        </div>
      </div>
    </div>
    <div ref="backdrop" id="backdrop"></div>
  </div>
</template>

<script>
import SearchResultsComponent from './SearchResultsComponent';
import SearchFiltersComponent from './SearchFiltersComponent';
import Multiselect from "vue-multiselect";
import Search from "../search";
import { search, searchFullUrl, fetchKeywords, fetchTopicCategories } from '../api';


/**
 * TODO
 * - cache pages as long as searchQuery is same
 */
export default {
  name: 'SearchMainComponent',

  components: {
    'search-results': SearchResultsComponent,
    'search-filters': SearchFiltersComponent,
    'multiselect': Multiselect,
    'search': Search,
  },

  data() {
    return {
      searchTerm: '',
      facets: {},
      results: [],
      count: null,
      searchQuery: '',
      resultsPerPage: 20,
      currentPage: 1,
      keywords: [],
      searchKeywords: '',
      selectedKeywords: [],
      pageSize: 20,
      loadingResults: false,
      resultPerPage: [
        { value: 20, text: '20' },
        { value: 50, text: '50' },
        { value: 100, text: '100' },
      ]
    };
  },

  computed: {
    showingResults() {
      const startCount = (this.currentPage - 1) * this.pageSize;
      const tempEndCount = this.currentPage * this.pageSize;
      const endCount = this.count > tempEndCount ? tempEndCount : this.count;
      const result = this.count ? 
        'Showing ' + startCount + ' - ' + endCount + ' of ' + this.count + ' results' :
        '0 results';
      return result;
    },
    showResultsCount() {
      return typeof this.count === 'number';
    },
  },

  mounted(){
    this.handleMobileSidebar();
    this.initiateKeywords();
  },

  methods: {
    handleSearch(result) {
      console.log('handle search!!!!!!', result);

      this.searchTerm = result.freeText.length > 0 ? '?search=' + result.freeText + '&' : '?';
      this.selectedKeywords = result.selectedKeywords.slice();
      console.log('this.searchTerm', this.searchTerm);
    },
    initiateKeywords() {
      const promises = [];
      let result = [];

      fetchKeywords().then(response => {
        // const keywords = response.data;
        // const keywordsNames = [];
        // for (let i = 0; i < keywords.length; i++) {
        //   const element = keywords[i];
        //   keywordsNames.push(element.name);
        // }

        // this.keywords = keywordsNames.sort();
        this.keywords = response.data;
      })
      .catch(error => {
        console.log(error);
      });
    },

    customLabel(option) {
      return `${option.name}`;
    },

    // addTag (newTag) {
    //   const tag = {
    //     name: newTag,
    //     code: newTag.substring(0, 2) + Math.floor((Math.random() * 10000000))
    //   }
    //   this.keywords.push(tag)
    //   this.selectedKeywords.push(tag)
    // },

    handleClickedSearchTerm() {
      this.currentPage = 1;
      this.handleUpdatedSearchTerm();
    },

    handleMobileSidebar(){
      let triggers = [this.$refs.sidebarTrigger, this.$refs.backdrop];
      let body = document.querySelector('body');

      triggers.forEach( function(element, index) {
        element.addEventListener('click', () => {
          body.classList.toggle('sidebaropen');
        })
      });
    },

    // removeSearchTerm() {
    //   this.currentPage = 1;
    //   this.searchTerm = '';
    //   this.selectedKeywords = [];
    //   this.handleUpdatedSearchTerm();
    // },

    /**
     * it is called by the result component by pressing the search button
     */
    handleUpdatedSearchTerm() {
      this.loadingResults = true;
      console.log(this.loadingResults)
      const resultSearchQuery = this.makeSearchQuery();
      this.doSearch(resultSearchQuery);
    },

    /**
     * it is called by the filter component (facets)
     */
    handleUpdatedFilter(searchQuery) {
      this.loadingResults = true;
      this.currentPage = 1;
      this.searchQuery = searchQuery;
      const resultSearchQuery = this.makeSearchQuery();

      this.doSearch(resultSearchQuery);
    },

    /**
     * used timeout because the change event precedes the model bind,
     * this means that the values of the current page is not the new one0
     * this way we move it at the end of the call stack, so that the value is correct
     */
    handlePageChange(ev) {
      this.loadingResults = true;

      setTimeout(() => {
        const resultSearchQuery = this.makeSearchQuery();
        this.doSearch(resultSearchQuery);
      })
    },

    /**
     * composes the search query based on search term, search query from filters and pagination
     */
    makeSearchQuery() {
      this.makeSearchTerm();
      let pagination = '?page=' + this.currentPage;
      let pageSizeQuery = this.pageSize !== 20 ? '&page_size=' + this.pageSize + '&' : '&';
      let resultSearchQuery = this.searchTerm + this.searchQuery;

      return pagination + pageSizeQuery + resultSearchQuery;
    },

    makeSearchTerm() {
      let result = '';

      this.selectedKeywords.map((keyword) => {
        result += `keyword=${keyword}&`;
      });

      this.searchKeywords = result;

      console.log('this.searchKeywords', this.searchKeywords);
    },

    /**
     * the actual search and updates the faces and result to the children components
     */
    doSearch(resultSearchQuery) {
      search(resultSearchQuery)
        .then((response) => {
          this.facets = response.data.facets;
          this.results = response.data.results;
          this.count = response.data.count;
          this.loadingResults = false;
        })
        .catch((error) => {
          console.log(error);
          this.loadingResults = false;
        });
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

#keywords-multiselect {
  position: relative;
  z-index: 6;
  flex-grow: 1;
}

.result-count {
  font-size: .8rem;
  color: #999;
  line-height: 2rem;
  display: flex;
  justify-content: space-between;
  .input-group {
    max-width: 15rem;
    max-height: 31px;
  }
  .input-group-text {
    font-size: .7rem;
  }
}


.spinner {
  z-index: 9999;
  position: absolute;
  top: -.5rem;
  bottom: 0;
  left: 0;
  right: .4rem;
  background: rgba(0, 0, 0, 0.03);
  display: flex;
  justify-content: flex-start;
  align-items: center;
  flex-direction: column;
  padding-top: 9rem;
  border-radius: .5rem;
}

.loader {
  border: 16px solid #f3f3f3;
  border-radius: 50%;
  border-top: 16px solid blue;
  border-right: 16px solid green;
  border-bottom: 16px solid red;
  border-left: 16px solid pink;
  width: 120px;
  height: 120px;
  -webkit-animation: spin 2s linear infinite; /* Safari */
  animation: spin 2s linear infinite;
}

/* Safari */
@-webkit-keyframes spin {
  0% { -webkit-transform: rotate(0deg); }
  100% { -webkit-transform: rotate(360deg); }
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

</style>
