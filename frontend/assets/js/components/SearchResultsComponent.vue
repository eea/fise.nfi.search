
<template>
  <div class="search-fise">

    <!-- result count -->
    <div class="result-count" v-if="showResultsCount">
      <p href="#" target="_self">{{ showingResults }}</p>
      <hr>
    </div>

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
        class="fise-search-modal"
      >
        <template slot="modal-title">
          <div class="d-flex align-items-start">
            <img
              :src="report"
              alt="report"
              width="60"
              height="70"
            >
            {{ selectedResult.title }}
          </div>
        </template>
        <template slot="modal-header-close">× Close</template>
        <template slot="modal-footer">
          <div v-if="selectedResult.download_url">
            <b-link
              :href="selectedResult.download_url"
              class="btn fise-search-download-link"
            >
              <i class="fa fa-download"></i>
              Download document ( {{ selectedResult.file_size | bytesToSize }} )
            </b-link>
          </div>
        </template>

        <div class="form-group row align-items-start">
          <div class="col-sm-2 col-form-label">Country</div>
          <div class="col-sm-10 col-form-label">
            <b-badge
              v-for="country in selectedResult.countries"
              :key="country"
              variant="default"
            >
              {{ country }}
            </b-badge>
          </div>
        </div>

        <div class="form-group row align-items-start">
          <div class="col-sm-2 col-form-label">Data set</div>
          <div class="col-sm-10 col-form-label">{{selectedResult.data_set | nfiExplain}}</div>
        </div>

        <div class="form-group row align-items-start">
          <div class="col-sm-2 col-form-label">Data type</div>
          <div class="col-sm-10 col-form-label">{{selectedResult.data_type}}</div>
        </div>

        <div class="form-group row align-items-start">
          <div class="col-sm-2 col-form-label">Description</div>
          <div class="col-sm-10 col-form-label">{{selectedResult.description}}</div>
        </div>

        <div class="form-group row align-items-start">
          <div class="col-sm-2 col-form-label">Resource format</div>
          <div class="col-sm-10 col-form-label">{{selectedResult.resource_type}}</div>
        </div>

        <div class="form-group row align-items-start">
          <div class="col-sm-2 col-form-label">Topic</div>
          <div class="col-sm-10 col-form-label">{{selectedResult.topic_category}}</div>
        </div>

        <div class="form-group row align-items-start">
          <div class="col-sm-2 col-form-label">NUTS levels</div>
          <div class="col-sm-10 col-form-label">
            <b-badge
              v-for="nut in selectedResult.nuts_levels"
              :key="nut"
              variant="default"
            >
              {{ nut | renameLevel }}
            </b-badge>
          </div>
        </div>

        <div class="form-group row align-items-start">
          <div class="col-sm-2 col-form-label">Keywords:</div>
          <div class="col-sm-10 col-form-label badge-container">
            <b-badge
              v-for="keyword in selectedResult.keywords"
              :key="keyword"
              variant="default"
              class="badge-outline"
            >{{ keyword }}</b-badge>
          </div>
        </div>

        <div class="form-group row align-items-start">
          <div class="col-sm-2 col-form-label">Info level</div>
          <div class="col-sm-10 col-form-label">{{selectedResult.info_level}}</div>
        </div>
      </b-modal>
    </div>

  </div>
</template>

<script>
import report from '../assets/report-icon.png';
import ListCustom from './ListCustom';
import filters from '../mixins/filters';

export default {
  name: 'SearchResultsComponent',

  components: {
    "list-custom": ListCustom,
  },

  props: {
    results: {},
    count: null,
    currentPage: null
  },

  mixins: [filters],

  computed: {
    showingResults() {
      const startCount = (this.currentPage - 1) * 20;
      const endCount = this.currentPage * 20;
      const result = this.count ? 
        'Showing ' + startCount + ' - ' + endCount + ' of ' + this.count + ' results' :
        '0 results';
      return result;
    },
    showResultsCount() {
      return typeof this.count === 'number';
    },
  },

  data() {
    return {
      prestineForm: true,
      selectedResult: null,
      modalShow: false,
      myDataList: JSON.parse(JSON.stringify(this.results)),
      report,
    };
  },

  methods: {
    handleSelectedResult(ev) {
      this.selectedResult = ev;
      this.modalShow = true;
    },
  },

  watch: {
    results: function(val) {
      this.myDataList = JSON.parse(JSON.stringify(val));
    }
  }
};
</script>

<style scoped lang="scss">

.nav-tabs .nav-link {
  border: 0;
}

.result-content {
  width: 100%;
}

.result-count {
  font-size: .8rem;
  color: #999;
  line-height: 2rem;

  hr {
    width: 15rem;
  }
}

svg path {
  fill: white;
  transform: rotate(0.1deg);
}
.fise-search-download-link {
  background-color: var(--fise-yellow);
  color: #111;
}
.badge-container {
  margin-left: -.5rem;
  margin-top: -.5rem;
}
.badge {
  font-size: inherit;
  font-weight: normal;
  color: #111;
}
.badge-outline {
  border: 1px solid #ddd;
  background-color: transparent;
  padding: .5em 1em;
  border-radius: 1em;
  margin-left: .5rem;
  margin-top: .5rem;
}
</style>
