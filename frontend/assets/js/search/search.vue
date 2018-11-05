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
  <div v-for="(item, index) in suggestedKeywords" @click="onKeywordClicked(index)">{{item}}</div>
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
import throttle from "lodash/throttle";

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
    allKeywords: Array,
  },
  data() {
    return {
      keywords: [
        "Romania",
        "roads",
        "2018",
        "2008",
        "nfi",
        "Growing Stock",
        "Forest Map / HRLevel Forest",
        "NFI (National Forest Inventory)"
      ],
      searchTerm: "",
      intermSerchTerm: "",
      whatToLookFor: "",
      indexOfKeyword: -1,
      afterSelectedKeyword: false,
      stillSelectingKeyword: false,
      suggestedKeywords: [],
      selectedKeywords: [],
      freeTextWords: [],
      freeText: ""
    };
  },
  mounted() {
    this.suggestedKeywords = this.keywords.slice();
  },
  methods: {
    onKeyUp: throttle(
      /**
       * for words only search for suggestions
       */
      function manageSearchTerm(ev) {
        if (
          ev.key !== "ArrowDown" &&
          ev.key !== "ArrowUp" &&
          ev.code !== "Space" &&
          ev.key !== "Escape" &&
          ev.key !== "Delete" &&
          ev.key !== "Backspace" &&
          ev.key !== "Enter"
        ) {
          this.handleWritingNewWords();
          this.handleWritingFirstWord();
          this.handleDeleteBySelectAllAndWriteOnTop();

          this.suggestedKeywords = this.filterByBeginingOfPhrase().slice();
        }
      },
      200
    ),
    handleWritingNewWords() {
      console.log("handleWritingNewWords");
      // if other words have already been entered take the last one to look for
      if (this.intermSerchTerm.length > 0) {
        const wordThatIsBeingEdited = this.isEditingWord();
        if (wordThatIsBeingEdited) {
          this.whatToLookFor = wordThatIsBeingEdited;
        } else {
          // not editing but writing in continuation of existing
          this.findWhatToLookForAsUserTypes();
        }
      }
    },
    handleWritingFirstWord() {
      console.log("handleWritingFirstWord");
      if (!this.intermSerchTerm.length > 0) {
        // if in the middle of writing first word, take it as is
        this.whatToLookFor = this.searchTerm;
      }
    },
    handleDeleteBySelectAllAndWriteOnTop() {
      console.log("handleDeleteBySelectAllAndWriteOnTop");
      // delete might have happend by replacing all with new words
      if (this.whatToLookFor === this.searchTerm) {
        this.intermSerchTerm = "";
        this.afterSelectedKeyword = false;
        this.stillSelectingKeyword = false;
        this.selectedKeywords = [];
        this.freeTextWords = [];
      }
    },
    isEditingWord() {
      console.log("isEditingWord NOT IMPLEMENTED");
      const allWordsInInterm = this.intermSerchTerm.split(' ');
      const allWordsInSearchTerm = this.searchTerm.split(' ');
      for (let i = 0; i < allWordsInSearchTerm.length; i++) {
        const searchWord = allWordsInSearchTerm[i];
        if(allWordsInInterm.indexOf(searchWord) === -1) {
          return searchWord;
        }
      }
      return null;
    },
    tryToSuggest() {
      console.log("identifyWordAndTryToSuggest NOT IMPLEMENTED");
      return false;
    },
    isEditingLastWord() {
      console.log("isEditingLastWord NOT IMPLEMENTED");
      return false;
    },
    isEditingAnyOtherWord() {
      console.log("isEditingAnyOtherWord NOT IMPLEMENTED");
      return false;
    },
    findWhatToLookForAsUserTypes() {
      const newAndOldInputsBySplit = this.searchTerm.split(
        this.intermSerchTerm
      );
      console.log("newAndOldInputsBySplit", newAndOldInputsBySplit);
      console.log("this.intermSerchTerm", this.intermSerchTerm);
      const newInputNoSpaces = newAndOldInputsBySplit[
        newAndOldInputsBySplit.length - 1
      ].trim();
      console.log("newInputNoSpaces", newInputNoSpaces);
      this.whatToLookFor = newInputNoSpaces;
    },
    onKeywordClicked(index) {
      this.indexOfKeyword = index;
      this.updateSelectedKeywords();
      this.indexOfKeyword = -1;
      this.intermSerchTerm = this.searchTerm;
      this.whatToLookFor = "";
      this.afterSelectedKeyword = false;
      this.stillSelectingKeyword = false;
    },
    /**
     * for the word (as it may be only a few letters, ex: 'lev' in 'Level 1', not '1' in 'Level 1')
     * it will look only at the begining
     */
    filterByBeginingOfPhrase() {
      let result = [];
      const compareWordLowerCase = this.whatToLookFor.toLowerCase();
      for (let index = 0; index < this.keywords.length; index++) {
        const keywordItem = this.keywords[index];
        const desiredLength = compareWordLowerCase.length;
        const keywordLowerCaseToMatch = keywordItem
          .substring(0, desiredLength)
          .toLowerCase();

        if (keywordLowerCaseToMatch === compareWordLowerCase) {
          result.push(keywordItem);
        }
      }

      return result;
    },
    /**
     * will select a choise, and replace it if keeps using the arrow
     */
    onKeyDownArrow() {
      if (this.suggestedKeywords.length > 0) {
        if (this.indexOfKeyword < this.suggestedKeywords.length - 1) {
          this.indexOfKeyword++;
        }

        this.updateSelectedKeywords();
        this.stillSelectingKeyword = true;
        this.afterSelectedKeyword = true;
        this.whatToLookFor = "";
      }
    },
    /**
     * will select a choise, and replace it if keeps using the arrow
     */
    onKeyUpArrow() {
      if (this.suggestedKeywords.length > 0) {
        if (this.indexOfKeyword > 0) {
          this.indexOfKeyword--;
        }

        this.updateSelectedKeywords();
        this.afterSelectedKeyword = true;
        this.stillSelectingKeyword = true;
        this.whatToLookFor = "";
      }
    },
    /**
     * add if first use of arrow, replace if consecutive uses
     */
    updateSelectedKeywords() {
      this.searchTerm =
        this.intermSerchTerm + this.suggestedKeywords[this.indexOfKeyword];

      if (this.stillSelectingKeyword && this.selectedKeywords.length > 0) {
        this.selectedKeywords.pop();
        this.selectedKeywords.push(this.suggestedKeywords[this.indexOfKeyword]);
      } else {
        this.selectedKeywords.push(this.suggestedKeywords[this.indexOfKeyword]);
      }
    },
    /**
     * new word, update list of suggested, and reset
     */
    onKeySpace() {
      const trimmedSearchTerm = this.searchTerm.trim();
      console.log("this.whatToLookFor", this.whatToLookFor);

      if (trimmedSearchTerm === "") {
        this.searchTerm = trimmedSearchTerm;
        this.intermSerchTerm = this.searchTerm;
        this.whatToLookFor = "";
        this.afterSelectedKeyword = false;
        this.stillSelectingKeyword = false;
      } else {
        // add any word as long as it is not ''
        // at this point a word means that it was not selected from the list
        if (this.whatToLookFor) {
          const theFoundKeyword = this.identifyKeyword();
          if (theFoundKeyword) {
            this.selectedKeywords.push(theFoundKeyword);
          } else {
            this.freeTextWords.push(this.whatToLookFor);
          }
        }
      }

      // reset
      this.indexOfKeyword = -1;
      this.suggestedKeywords = this.keywords.slice();
      this.intermSerchTerm = this.searchTerm;
      this.whatToLookFor = "";
      this.afterSelectedKeyword = false;
      this.stillSelectingKeyword = false;


      for (let i = 0; i < this.freeTextWords.length; i++) {
        const word = this.freeTextWords[i];
        this.freeText += word + ' ';
      }
      this.$emit('madeKeywords', {selectedKeywords: this.selectedKeywords, freeText: this.freeText.trim()});
    },
    identifyKeyword() {
      for (let i = 0; i < this.keywords.length; i++) {
        const lowerdTrimmedKeyword = this.keywords[i].trim().toLowerCase();
        const lowerdTrimmedWordToLookFor = this.whatToLookFor
          .trim()
          .toLowerCase();

        if (lowerdTrimmedKeyword === lowerdTrimmedWordToLookFor) {
          return this.keywords[i];
        }
      }
      return null;
    },
    /**
     * use this for selectedKeywords and for freeTextWords,
     * easyer to to it at the end (click on search button) than implement complex altgorithm to determine it while writing
     */
    makeListOfKeywordsUnique(originalList) {
      const result = [];
      for (let i = 0; i < originalList.length; i++) {
        const item = originalList[i];
        if (result.indexOf(item) === -1) {
          result.push(item);
        }
      }
      return result;
    },
    /**
     * works:
     * - delete/backspace while writing before " "
     * - reset on delete all
     * TODO:
     * - identify deleted word
     * - re-suggest the word that is being deleted if starts to be recognized
     * - remove if completelly deleted or replace as it is when editing it is done, on " "
     */
    onKeyDelete(ev) {
      this.indexOfKeyword = -1;

      if (this.searchTerm) {
        console.log("A");
        if (this.deletingWhileWritingNewWords()) {
          console.log("B");
          const newAndOldInputsBySplit = this.searchTerm.split(
            this.intermSerchTerm
          );
          console.log("B newAndOldInputsBySplit", newAndOldInputsBySplit);
          const newInputNoSpaces = newAndOldInputsBySplit[
            newAndOldInputsBySplit.length - 1
          ].trim();
          console.log("B newInputNoSpaces", newInputNoSpaces);
          this.whatToLookFor = newInputNoSpaces;
          console.log("B this.whatToLookFor", this.whatToLookFor);
          this.suggestedKeywords = this.filterByBeginingOfPhrase().slice();
        } else {
          console.log("C");

          // deleted words that already have been marked as keywords or free text
          // this.whatToLookFor = this.searchTerm;
        }
      } else {
        console.log("R");

        this.reset(); // all words have been deleted
      }
    },
    deletingWhileWritingNewWords() {
      const isInterimPartOfSeachTerm =
        this.searchTerm.substring(0, this.intermSerchTerm.length) ===
        this.intermSerchTerm;
      return this.intermSerchTerm.length > 0 && isInterimPartOfSeachTerm;
    },
    /**
     * @enter
     * done at the end and remove all deleted keywords and free text, no need for complicated algorithm
     * at the point of editing
     */
    updateWordsList() {
      const allWordsNow = this.searchTerm.split(" ");
      const resultUpdatedKeywords = [];
      const resultUpdatedFreeTextWords = [];
      for (let i = 0; i < this.selectedKeywords.length; i++) {
        const keyword = this.selectedKeywords[i];
        if (this.allWordsNow.indexOf(keyword) > -1) {
          resultUpdatedKeywords.push(keyword);
        }
      }
      for (let i = 0; i < this.freeTextWords.length; i++) {
        const freeTextWord = this.freeTextWords[i];
        if (this.allWordsNow.indexOf(freeTextWord) > -1) {
          resultUpdatedFreeTextWords.push(freeTextWord);
        }
      }
      this.selectedKeywords = resultUpdatedKeywords.slice();
      this.freeTextWords = resultUpdatedFreeTextWords.slice();
    },
    reset() {
      this.suggestedKeywords = this.keywords.slice();
      this.indexOfKeyword = -1;
      this.intermSerchTerm = this.searchTerm;
      this.whatToLookFor = "";
      this.afterSelectedKeyword = false;
      this.stillSelectingKeyword = false;
      this.selectedKeywords = [];
      this.freeTextWords = [];
    },
    /**
     * will show the dropdown of suggestions (limited if whatToLookFor is to generic???)
     */
    activate() {
      console.log("TODO activate implement");
    },
    /**
     * will hide the dropdown of suggestions
     */
    deactivate() {
      console.log("TODO deactivate implement");
    }
  }
};
</script>

<style>
</style>
