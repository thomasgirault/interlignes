class Corpus {
    constructor() {

        this.extra_spaces;

        this.interlude_play;

        this.current_paragraph = 0;
        this.current_ponctuation_paragraph = 0;
        // this.new_params;
        // this.params

        this.corpus = {}
        this.get_corpus("tentative")
        this.get_corpus("ponctuation")
        this.get_corpus("MERCI2")
        // this.tentative + this.ponctuation + this.merci
    }

    get_corpus(corpus_name) {
        fetch("/corpus/" + corpus_name)
            .then(response => response.json())
            .then((data) => {
                this.corpus[data['corpus']] = data['data'];
            });
    }

    get_paragraph() {
        if (params['ponctuation_proba'] > Math.random() * 100)
            return this.generate_punctuation();
        else
            return this.generate_text();

            // gérer les mercis et les la ponctuation
    }

    generate_punctuation() {
        var texte = this.corpus['ponctuation'][this.current_ponctuation_paragraph];
        this.current_ponctuation_paragraph += 1;
        this.current_ponctuation_paragraph %= this.corpus['ponctuation'].length;
        return texte
    }

    generate_text() {
        var texte = this.corpus['tentative'][this.current_paragraph]; // + " ".repeat(params['extra_spaces']);
        this.current_paragraph += 1;
        if (this.current_paragraph > this.corpus['tentative'].length - 1) {
            this.current_paragraph = 0
            console.log("fin de texte", params["interlude_play"]);
            if (params["video_ok"])
                params["interlude_play"] = 1;
        }
        return texte
    }

}