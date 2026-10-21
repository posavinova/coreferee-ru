# Сoreferee-ru

**Russian-language coreference resolution based on Coreferee and spaCy.**

------------------------------------------------------------------------

## About

`Coreferee-ru` is a Russian-language adaptation of the [Coreferee](https://github.com/richardpaulhudson/coreferee) framework.
It preserves the core Coreferee interface, adding rules and a 3 trained models for processing Russian (sm, md, lg).
Current compatibility tested for spaCy version 3.8.0

> **Licensing notice:** the licenses for the original Coreferee source code and the training data used by this project differ, which is why a separate repository had to be created.
> Before distributing the package, model weights, or training data, review the applicable terms for each component.

## Main features

-   Detects coreference chains in Russian text

-   Integrates into a spaCy processing pipeline

Results depend on the quality of the syntactic and morphological analysis produced by the selected spaCy model. Coreference resolution cannot guarantee the correct interpretation of every ambiguous reference.

## Model performance

<table style="text-align:center; vertical-align:middle">
  <tr><td rowspan="2">Training corpora</td><td rowspan="2">Total words in training corpora</td><td colspan="2"><code>*_lg</code> models</td><td colspan="2"><code>*_md</code> models</td><td colspan="2"><code>*_sm</code> models</td></tr>  
  <tr><td align="center">Anaphors in 20%</td><td align="center">Accuracy (%)</td><td align="center">Anaphors in 20%</td><td align="center">Accuracy (%)</td><td align="center">Anaphors in 20%</td><td align="center">Accuracy (%)</td></tr>
  <tr><td align="center"><a href="https://github.com/Koziev/NLP_Datasets/tree/master/Anacoref">RuCoref</a> (<a href=https://github.com/Horncn/RuCoref-Spacy-adaptation>modified</a><sup>*</sup>) & <a href=https://github.com/dialogue-evaluation/RuCoCo-2023>RuCoCo</a></td>
  <td align="center">1226212</td><td align="center">5700—8600</td><td align="center">73.67</td><td align="center">5700—8600</td><td align="center">73.38</td><td align="center"><b>5700—8600</b></td><td align="center"><b>76.14</b></td></tr>
</table>

*\* Modification reduces the amount of conflicts between original annotation and spaCy models*

## Installation

1.  Install the package:

``` bash
python -m pip install coreferee-ru
```

2. Install a supported Russian spaCy model, e.g.:

``` bash
python -m spacy download ru_core_news_lg
```


## Quick start

``` python
import spacy
import coreferee_ru  # registers the spaCy component

nlp = spacy.load("ru_core_news_lg")
nlp.add_pipe("coreferee_ru")

doc = nlp(
    "Хотя они добрались до их дома, Петр и Анна грустили. Он ушел спать. Она взяла свою любимую книгу, которую купила давно."
)
```

```
>>> doc._.coref_chains.print()
0: они(1), их(4), [Петр(7); Анна(9)]
1: Петр(7), Он(12)
2: Анна(9), Она(16), свою(18)
3: книгу(20), которую(22)
>>>
>>> doc[9]._.coref_chains.print()
0: они(1), их(4), [Петр(7); Анна(9)]
2: Анна(9), Она(16), свою(18)
>>>
>>> doc._.coref_chains.resolve(doc[4])
[Петр, Анна]
```

## API usage

-   `doc._.coref_chains` - document's coreference-chain container;

-   `doc._.coref_chains.print()` - prints the chains in a readable format;

-   `doc._.coref_chains.resolve(token)` - retrieves the most specific mention or mentions referred to by a token.


## Credits and provenance

**Сoreferee-ru** builds on the architecture and interface of
**Coreferee**, created by [Richard Paul
Hudson](https://github.com/richardpaulhudson).


## Links

-   [Coreferee](https://github.com/richardpaulhudson/coreferee)
-   [Richard Paul Hudson](https://github.com/richardpaulhudson)
-   [spaCy](https://spacy.io/)
-   [RuCoref](https://github.com/Koziev/NLP_Datasets/tree/master/Anacoref)
-   [RuCoCo](https://github.com/dialogue-evaluation/RuCoCo-2023)
