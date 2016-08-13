# 自定义分词器 nGram
https://www.elastic.co/guide/en/elasticsearch/reference/1.7/analysis-ngram-tokenizer.html

https://www.elastic.co/guide/en/elasticsearch/reference/1.7/analysis-edgengram-tokenizer.html

## 自定义nGram分词器
```
public XContentBuilder nGramAnalyzer() throws IOException{
        XContentBuilder settings = XContentFactory.jsonBuilder()
                .startObject()
                .startObject("index")
                .startObject("analysis")
                    .startObject("tokenizer")
                        .startObject("my_ngram_tokenizer")
                            .field("type", "nGram")
                            .field("min_gram", "2")
                            .field("max_gram", "20")
                            .field("token_chars", "")
                        .endObject()
                    .endObject()
                    .startObject("analyzer")
                        .startObject("search_analyzer")
                            .field("tokenizer", "my_ngram_tokenizer")
                            .field("type", "custom")
                            .field("filter", "lowercase")  // 转成小写
                        .endObject()
                    .endObject()
                .endObject()
                .endObject()
                .endObject();

        return settings;
    }

    // token_chars : letter, digit, whitespace, punctuation, symbol, unassigned, uppercase_letter, lowercase_letter, titlecase_letter, modifier_letter, other_letter, non_spacing_mark, enclosing_mark, combining_spacing_mark, decimal_digit_number, letter_number, other_number, space_separator, line_separator, paragraph_separator, control, format, private_use, surrogate, dash_punctuation, start_punctuation, end_punctuation, connector_punctuation, other_punctuation, math_symbol, currency_symbol, modifier_symbol, other_symbol, initial_quote_punctuation, final_quote_punctuation
```

## 创建索引
```
transportClient.admin().indices().prepareCreate(index).setSettings(nGramAnalyzer()).execute().actionGet();
```

## 创建mapping
```

```

## StackOverflow
http://stackoverflow.com/questions/17569938/analyzer-not-found-exception-while-creating-an-index-with-mapping-and-settings
