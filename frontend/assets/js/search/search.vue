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
</div>

</template>

<script>
import throttle from "lodash/throttle";

export default {
  name: "vue-search",
  props: {
    allKeywords: Array
  },
  data() {
    return {
      keywords: [],
      searchTerm: "",
      intermSerchTerm: "",
      whatToLookFor: "",
      indexOfKeyword: -1,
      afterSelectedKeyword: false,
      suggestedKeywords: [],
      active: false
    };
  },
  mounted() {
    for (let i = 0; i < this.allKeywords.length; i++) {
      const element = this.allKeywords[i];
      this.keywords.push(element.name);
    }
    this.suggestedKeywords = this.keywords.slice();
  },
  methods: {
    onKeyUp: throttle(
      /**
       * search for suggestions only for words
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
          if (this.replacedWords()) {
            this.intermSerchTerm = "";
          }
          this.identifyWhatToSuggest();
          this.attemptToSuggest();
        }
      },
      200
    ),
    /**
     * it is possible that the user selects all and presses a key or pastes a word,
     */
    replacedWords() {
      return (
        this.searchTerm.substring(0, this.intermSerchTerm.length) !==
        this.intermSerchTerm
      );
    },
    /**
     * for now it will only look for the last word
     * TODO try to suggest while user edits words somewhere inside the searchTerm
     */
    identifyWhatToSuggest() {
      this.identifyLasIncompleteWord();
    },
    /**
     * takes the last word
     */
    identifyLasIncompleteWord() {
      const allWordsInSearchTerm = this.searchTerm.split(" ");
      this.whatToLookFor =
        allWordsInSearchTerm[allWordsInSearchTerm.length - 1];
    },
    attemptToSuggest() {
      this.suggestedKeywords = this.filterResults().slice();
    },
    /**
     * for the word (as it may be only a few letters, ex: 'lev' in 'Level 1', not '1' in 'Level 1')
     * it will look only at the start of the keyword
     */
    filterResults() {
      let result = [];
      const compareWordLowerCase = this.whatToLookFor.toLowerCase();
      if (this.whatToLookFor) {
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
      } else {
        result = this.keywords.slice();
      }

      return result;
    },
    /**
     * handle for click on result
     */
    onKeywordClicked(index) {
      this.indexOfKeyword = index;
      this.updateWithSelected();
      this.reset();
    },
    /**
     * handle for key arrow down
     * will select a choice, and replace the last word
     */
    onKeyDownArrow() {
      if (this.suggestedKeywords.length > 0) {
        if (this.indexOfKeyword < this.suggestedKeywords.length - 1) {
          this.indexOfKeyword++;
        }
        this.updateWithSelected();
      }
    },
    /**
     * will replace the partial word that is being written
     * now it will replace the last
     * TODO replace wherever it is being written
     */
    updateWithSelected() {
      this.replaceLastPartialWordWithSelected();
    },
    /**
     * replace last partial word
     */
    replaceLastPartialWordWithSelected() {
      this.searchTerm = (
        this.intermSerchTerm +
        " " +
        this.suggestedKeywords[this.indexOfKeyword]
      ).trim();
    },
    /**
     * handle for key arrow up
     * will select a choice, and replace the last word
     */
    onKeyUpArrow() {
      if (this.suggestedKeywords.length > 0) {
        if (this.indexOfKeyword > 0) {
          this.indexOfKeyword--;
        } else if (this.indexOfKeyword === -1) {
          this.indexOfKeyword++;
        }
        this.updateWithSelected();
      }
    },

    /**
     * handle for space key
     * reset and make list of keywords
     * will emit the event of lists made
     */
    onKeySpace() {
      this.intermSerchTerm = this.searchTerm.trim();
      this.makeKeywordsAndFreeTexts();
      this.reset();
    },
    /**
     * will make the lists of unique keywords used and unique free text words
     * emit
     */
    makeKeywordsAndFreeTexts() {
      let selectedKeywords = [];
      let freeTextWords = [];
      let freeText = "";
      let tempSearchTerm = this.searchTerm;
      let index = 0;

      for (let i = 0; i < this.keywords.length; i++) {
        const keyword = this.keywords[i];

        if (isKeyword(keyword)) {
          selectedKeywords.push(keyword);
          tempSearchTerm = removeKeywordFromSearchTerm(keyword, tempSearchTerm);
        }
      }
      const allFreeWords = tempSearchTerm.trim().toLowerCase().split(' ');

      for (let i = 0; i < allFreeWords.length; i++) {
        const freeWord = allFreeWords[i];
        if(freeTextWords.indexOf(freeWord) === -1) {
          freeTextWords.push(freeWord);
        }
      }
      freeText = '';
      for (let i = 0; i < freeTextWords.length; i++) {
        const element = freeTextWords[i];
        freeText += element + ' ';
      }
      freeText = freeText.trim();

      this.$emit('madeKeywords', {selectedKeywords: selectedKeywords, freeText: freeText});

      function isKeyword(keyword) {
        let lengthOfKeyword = 0;
        const smallSearchTerm = tempSearchTerm.toLowerCase();
        let found = false;
        let trimmedSmallKeyword = keyword.trim().toLowerCase();
        index = -1;

        while (
          index + trimmedSmallKeyword.length < smallSearchTerm.length &&
          !found
        ) {
          index++;
          found =
            smallSearchTerm.substring(
              index,
              trimmedSmallKeyword.length + index
            ) === trimmedSmallKeyword;
        }

        return found;
      }
      function removeKeywordFromSearchTerm(keyword, phrase) {
        let index = -1;
        let tempPhrase = phrase;

        while (index + keyword.length < phrase.length) {
          index++;
          const partWord = tempPhrase.substring(index, keyword.length + index);
          const found = partWord.toLowerCase() === keyword.toLowerCase();
          if(found) {
            tempPhrase = tempPhrase.replace(partWord, '');
          }
        }
          
        return tempPhrase;
      }
    },
    /**
     * handle for delete/backspace
     * will try to suggest for word that is being deleted while writing it
     */
    onKeyDelete(ev) {
      this.indexOfKeyword = -1;

      if (this.searchTerm) {
        const allWords = this.searchTerm.split(' ');
        const lastWord = allWords[allWords.length - 1];

        this.whatToLookFor = lastWord;
        this.suggestedKeywords = this.filterResults().slice();
      } else {
        this.reset(); // all words have been deleted
      }
    },

    reset() {
      this.suggestedKeywords = this.keywords.slice();
      this.indexOfKeyword = -1;
      this.whatToLookFor = "";
      this.intermSerchTerm = this.searchTerm.trim();
      this.afterSelectedKeyword = false;
    },
    /**
     * will show the dropdown of suggestions
     */
    activate() {
      this.active = true;
    },
    /**
     * will hide the dropdown of suggestions
     */
    deactivate() {
      this.active = false;
    }
  }
};
</script>

<style>
</style>
