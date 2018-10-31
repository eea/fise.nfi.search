<template>
<div>
  <input
    type="text"
    class="search-input"
    id="inputSearch"
    placeholder="Search..."
    v-model="searchTerm"
    @keyup="onKeyUp"
    @keyup.self.down.prevent="onKeyDownArrow"
    @keyup.self.up.prevent="onKeyUpArrow"
    @keyup.delete="onKeyDelete"
    @keyup.space="onKeySpace"
    @keyup.esc="deactivate"
    @focus.prevent="activate"
    @blur.prevent="deactivate"
    style="width: 100%;"
  >
  <div v-for="item in suggestedKeywords">{{item}}</div>
  <hr>
  <hr>
  <div v-for="item in keywords">{{item}}</div>
  <hr>
  <div>searchTerm for: {{searchTerm}}</div>
  <hr>
  <div>Index is: {{indexOfKeyword}}</div>
  <hr>
  <div>whatToLookFor is: {{whatToLookFor}}</div>
  <hr>
  <div>intermSerchTerm is: {{intermSerchTerm}}</div>
  <hr>
  <div>afterSelectedKeyword is: {{afterSelectedKeyword}}</div>
  <hr>
  <div>stillSelectingKeyword is: {{stillSelectingKeyword}}</div>
  <hr>
  <div>selectedKeywords are: {{selectedKeywords}}</div>
  <hr>
  <div>freeTextWords are: {{freeTextWords}}</div>
  <hr>
  <div>freeText is: {{freeText}}</div>
</div>

</template>

<script>
// import filterResults from './filterResults';
import throttle from 'lodash/throttle';

export default {
  name: "vue-search",
  props: {
    // /**
    //  * name attribute to match optional label element
    //  * @default ''
    //  * @type {String}
    //  */
    // name: {
    //   type: String,
    //   default: ""
    // }
  },
  data() {
    return {
      keywords: [
        'Romania',
        'roads',
        '2018',
        '2008',
        'nfi',
        'Growing Stock',
        'Forest Map / HRLevel Forest',
        'NFI (National Forest Inventory)',
      ],
      searchTerm: '',
      intermSerchTerm: '',
      whatToLookFor: '',
      indexOfKeyword: -1,
      afterSelectedKeyword: false,
      stillSelectingKeyword: false,
      suggestedKeywords: [],
      selectedKeywords: [],
      freeTextWords: [],
      freeText: '',
    }
  },
  mounted() {
    this.suggestedKeywords = this.keywords.slice();
  },
  methods: {
    onKeyUp: throttle(
      function manageSearchTerm(ev) {
        if(ev.key !== 'ArrowDown' 
          && ev.key !== 'ArrowUp' 
          && ev.code !== 'Space' 
          && ev.key !== 'Escape' 
          && ev.key !== 'Enter') {
          if(this.intermSerchTerm.length > 0) {
            const newAndOldInputsBySplit = this.searchTerm.split(this.intermSerchTerm);
            const newInputNoSpaces = newAndOldInputsBySplit[newAndOldInputsBySplit.length - 1].trim();
            this.whatToLookFor = newInputNoSpaces;
          } else {
            this.whatToLookFor = this.searchTerm;
          }

          this.suggestedKeywords = this.filterByBeginingOfPhrase().slice();
        }
      },
      200
    ),
    filterByBeginingOfPhrase() {
      let result = [];
      const compareWordLowerCase = this.whatToLookFor.toLowerCase();
      for (let index = 0; index < this.keywords.length; index++) {
        const keywordItem = this.keywords[index];
        const desiredLength = compareWordLowerCase.length;
        const keywordLowerCaseToMatch = keywordItem.substring(0, desiredLength).toLowerCase();

        if (keywordLowerCaseToMatch === compareWordLowerCase) {
          result.push(keywordItem);
        }
      }

      return result;
    },
    onKeyDownArrow() {
      if(this.suggestedKeywords.length > 0) {
        if(this.indexOfKeyword < this.suggestedKeywords.length -1) {
          this.indexOfKeyword++;
        }

        this.updateSelectedKeywords();
        this.stillSelectingKeyword = true;
        this.afterSelectedKeyword = true;
        this.whatToLookFor = '';
      }
    },
    onKeyUpArrow() {
      if(this.suggestedKeywords.length > 0) {
        if(this.indexOfKeyword > 0) {
          this.indexOfKeyword--;
        }

        this.updateSelectedKeywords();
        this.afterSelectedKeyword = true;
        this.stillSelectingKeyword = true;
        this.whatToLookFor = '';
      }
    },
    updateSelectedKeywords() {
      this.searchTerm = this.intermSerchTerm + this.suggestedKeywords[this.indexOfKeyword];

      if(this.stillSelectingKeyword && this.selectedKeywords.length > 0) {
        this.selectedKeywords.pop();
        this.selectedKeywords.push(this.suggestedKeywords[this.indexOfKeyword]);
      } else {
        this.selectedKeywords.push(this.suggestedKeywords[this.indexOfKeyword]);
      }

    },
    onKeySpace() {
      // nu suggestions means free text
      if(this.suggestedKeywords.length === 0) {
        this.freeTextWords.push(this.whatToLookFor);
      }
      // at this point a keyword has been selected
      if(this.afterSelectedKeyword) {
        this.suggestedKeywords = this.keywords.slice();
        this.indexOfKeyword = -1;
      }
      // reset
      this.intermSerchTerm = this.searchTerm;
      this.whatToLookFor = '';
      this.afterSelectedKeyword = false;
      this.stillSelectingKeyword = false;
    },
    /**
     * use this for selectedKeywords and for freeTextWords,
     * easyer to to it at the end (click on search button) than implement complex altgorithm to determine it while writing
     */
    makeListOfKeywordsUnique(originalList) {
      const result = [];
      for (let i = 0; i < originalList.length; i++) {
        const item = originalList[i];
        if(result.indexOf(item) === -1) {
          result.push(item);
        }
      }
      return result;
    },
    /**
     * 
     */
    onKeyDelete() {
      console.log('TODO onKeyDelete implement');
      this.indexOfKeyword = -1;
    },
    /**
     * will show the dropdown of suggestions (limited if whatToLookFor is to generic???)
     */
    activate() {
      console.log('TODO activate implement');
    },
    /**
     * will hide the dropdown of suggestions
     */
    deactivate() {
      console.log('TODO deactivate implement');
    },
  },
};
</script>

<style>
</style>
