class Ligne {
  constructor(texte) {
    this.segLength = 70;                                 // **change** float to var
    this.maxLen = 30;
    this.minFontSize = 20;
    this.maxFontSize = 200;

    this.x = new Array(this.segLength);  // **change** float[] x = new float[20] to new Array(20)
    this.y = new Array(this.segLength);  // **change** float[] y = new float[20] to new Array(20)
    this.letterSizes = new Array(this.segLength);
    this.texte = texte;
    this.ligne = "";
    this.current = 0;
    this.scrollText(0);
    this.initPositions();
  }

  initPositions() {
    for (var i = 0; i < this.x.length; i++) {         // initialize the array
      this.x[i] = 0;
      this.y[i] = 0;
      this.letterSizes[i] = 0;
    }
  }

  scrollText(i) {
    this.ligne = this.texte.substr(i, this.segLength);
    this.ligne = this.ligne.split('').reverse().join('');
  }

  setTexte(t) {
    this.texte = t;
  }


  drawLetter(i, xin, yin) {
    var dx = xin - this.x[i];
    var dy = yin - this.y[i];
    var angle = atan2(dy / 2, dx / 2);
    var letter = String(this.ligne[i]);
    var speed_norm = Math.sqrt(dx * dx + dy * dy);
    
    if(i == 0){
      // var letterSize = Math.min(100, int(speed_norm));
      var letterSize = Math.min(this.maxFontSize, this.minFontSize + int(speed_norm) / 2);
    }
    // console.log(speed_norm);
    // var stepSize = textWidth(letter, 170);

    var color = int(255. / (1 + Math.sqrt(0.01 * i)/2.))

    this.x[i] = xin - cos(angle) * this.maxLen;
    this.y[i] = yin - sin(angle) * this.maxLen;

    push();
    translate(this.x[i], this.y[i]);
    rotate(angle);
    try {
      fill(color);
      textSize(this.letterSizes[i]);
      text(letter, 0, 0);
    }
    catch (err) {
      console.log(err.message);
    }
    pop();
    return letterSize;
  }

  draw(x, y){
    var letterSize = this.drawLetter(0, x, y);
    if (this.current + 0.05 < this.ligne.length){
      this.letterSizes.unshift(letterSize);
      this.letterSizes.pop();
      this.scrollText(this.current);
    }
    // var dx = x - this.x[0];
    // var dy = y - this.y[0];
    // il faut créer des frames intermédiaires ici
    for (var n = 0; n < this.ligne.length - 1; n++) {
      this.drawLetter(n + 1, this.x[n], this.y[n]);
    }
    this.current = (this.current + 0.05) % this.ligne.length;
  }

}