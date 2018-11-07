<template>
<div class="custom-search">
  <b-input-group>

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
    @keyup.enter="onKeyEnter"
    @keyup.esc="deactivate"
    @focus.prevent="activate"
    @blur.prevent="deactivate"
    style="width: 100%;"
  >
  <div v-if="active && suggestedKeywords.length > 0" class="search-results">
    <div v-for="(item, index) in suggestedKeywords" @click="onKeywordClicked(index)">{{item}}</div>
  </div>


  <!-- search button -->
  <b-input-group-append>
    <b-btn
      variant="primary"
      v-on:click="handleClickedSearch"
    >Go</b-btn>
  </b-input-group-append>

  </b-input-group>

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
    this.keywords = this.allKeywords.sort().slice();
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
    handleClickedSearch() {
      this.makeKeywordsAndFreeTexts();
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
    onKeyEnter() {
      this.intermSerchTerm = this.searchTerm.trim();
      this.makeKeywordsAndFreeTexts();
      this.reset();
    },
    /**
     * handle for space key
     * reset and make list of keywords
     * will emit the event of lists made
     */
    onKeySpace() {
      this.intermSerchTerm = this.searchTerm.trim();
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

      // TODO refactor method to be immutable, modular and single responsability
      this.$emit('searchForKeywords', {selectedKeywords: selectedKeywords, freeText: freeText});

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
     * the dissable happens before the cick => the wait for 100 ms
     */
    deactivate() {
      setTimeout(() => {
        this.active = false;
      }, 200);
    }
  }
};
</script>

<style  lang="scss">
.custom-search {
  position: relative;
  height: 100%;
}
.custom-search input {
  width: 100%;
  height: 100%;
  border: none;
  padding-left: 1rem;
}

.search-results {
  position: absolute;
  background: white;
  width: 100%;
  top: 39px;
  left: -1px;
  border: 1px solid white;
  padding: 1rem;
  padding-top: 0;
  max-height: 300px;
  overflow: auto;
  box-shadow: 1px 1px 3px #aaa;
}

.search-results div {
  cursor: pointer;
  border: 1px solid #fff;
}

.search-results div:hover {
  border: 1px solid #eee;
}
.slinput {
  position: relative;
  border: 1px solid #fff;
  background-color: #fff;
  width: 100%;
      border-radius: 0.25em;
  .input-group-append {
    margin-left: 0;
    order: 2;
  }

  #inputSearch {
    width: initial!important;
    height: initial;
    flex-grow: 1;
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
</style>
