# llama.cpp System One API reference

Source: [llama.cpp server README](https://github.com/ggml-org/llama.cpp/blob/08246a28f6000100433d297c4e037c02e9d2d464/tools/server/README.md#post-v1systemone-typesafe-compatible-system-one-api)

Commit: `08246a28f6000100433d297c4e037c02e9d2d464`

---

### POST `/v1/systemone`: TypeSafe-compatible System One API

Answers typed questions about a `state` with a decision model.

Follows the [TypeSafe API](https://docs.typesafe.ai/api), streaming is not supported. Multimodal input is an extension to this API, see the [OpenJev multimodal API](https://jev-skills.github.io/openjev-multimodal/api) for reference.

*Options:*

`state`: The content to evaluate. Can be a string, an object or an array. A value that is not a string is given to the model as JSON text. For lfm2-d1 and lfm2-d1-omni, it can be `null`, for example to ask about images only.

`files`: Optional. An array of input files, the maximum number may be limited depending on the model. Each one is a data URL (`data:image/...;base64,...`). For audio-capable models, it can be audio clips (`data:audio/...;base64,...`). See the image input section below.

`images`: Optional. An alias of `files`.

`questions`: An object that maps a question id to a question. Each question has these fields:

- `type`: One of `choice`, `score`, `noul`.
- `instructions`: The question. Can be a string, an object or an array.
- `criteria`: The possible answers, the shape depends on `type`:
  - `choice`: An object that maps each option to its description. The description can be `null`.
  - `score`: An array of 2 to 10 level descriptions, lowest level first.
  - `noul`: Optional. An object with the descriptions of `true` and `false`.

The questions of a request are answered independently, an answer does not depend on the other questions. The exception is clef: it reads all the questions in one prompt and decides them jointly.

The number of options of a `choice` question is limited by the model, for example: 52 for openjev, 255 for laya, clef, pplx-decider, lfm2-d1 and lfm2-d1-omni. For laya, long questions and options are truncated to the token budget the model was trained with.

For laya, clef and lfm2-d1-omni, the whole prompt is evaluated in one batch: it must fit in `--ubatch-size`. An lfm2-d1-omni prompt is cut to 16384 tokens. A server that runs clef only serves this endpoint, text generation is not available.

*Image input:*

Image input needs a model that supports it (for example: openjev, clef, pplx-decider, lfm2-d1, lfm2-d1-omni) and its multimodal projector, see `--mmproj`.

Images can be given in two ways, and both can be used in the same request:

- The `files` field, or its alias `images`.
- A `state` made of chat messages, either an array of messages or an object with a `messages` array. An `image_url` part in the `content` of a message is taken as an image, in the same format as chat completions. Only data URLs are accepted. For lfm2-d1-omni, an `input_audio` part is taken as an audio clip, as base64 data.

All the images are placed before the state in the prompt, the ones from `files` and `images` first. The image parts are removed from the state.

*Response:*

`answers`: An object that maps each question id to its answer. The fields depend on the question type:

- `choice`:
  - `choice`: The option with the highest probability.
  - `probabilities`: The probability of each option, they sum to 1.
  - `confidence`: A value from 0 to 1, where 0 means all options are equally likely.
- `score`:
  - `score`: The expected level index, weighted by probability. It can be between two levels.
  - `legend`: The description of each level index.
  - `probabilities`: The probability of each level index, they sum to 1.
  - `confidence`: A value from 0 to 1.
- `noul`:
  - `noul`: The probability that the answer is true.

`noul`, derived from *Bernoulli*, is the yes/no question type. Its answer is a
number from 0 to 1 representing the probability of yes or true.

`usage`: `input_tokens` is the number of prompt tokens of all questions. `output_tokens` is always 0.

The probabilities are scaled with the temperatures stored in the model file. They are not guaranteed to be calibrated for your data.

*Examples:*

```shell
curl http://127.0.0.1:8080/v1/systemone \
    -H "Content-Type: application/json" \
    -d '{
        "state": "Customer message: I was charged twice for my order last week and nobody has replied.",
        "questions": {
            "route": {
                "type": "choice",
                "instructions": "Which team should handle this?",
                "criteria": {"billing": null, "shipping": null, "technical": null}
            },
            "angry": {
                "type": "noul",
                "instructions": "Is the customer angry?"
            },
            "urgency": {
                "type": "score",
                "instructions": "How urgent is this?",
                "criteria": ["can wait", "this week", "today", "right now"]
            }
        }
    }' | jq
```

Response (values are shortened):

```json
{
  "model": "openjev",
  "answers": {
    "route": {
      "type": "choice",
      "choice": "billing",
      "probabilities": {"billing": 0.9998, "shipping": 0.0001, "technical": 0.0001},
      "confidence": 0.9997
    },
    "angry": {
      "type": "noul",
      "noul": 0.6328
    },
    "urgency": {
      "type": "score",
      "score": 2.0858,
      "legend": {"0": "can wait", "1": "this week", "2": "today", "3": "right now"},
      "probabilities": {"0": 0.0023, "1": 0.116, "2": 0.6753, "3": 0.2064},
      "confidence": 0.673
    }
  },
  "usage": {
    "input_tokens": 239,
    "output_tokens": 0
  }
}
```

Example with an image:

```shell
curl http://127.0.0.1:8080/v1/systemone \
    -H "Content-Type: application/json" \
    -d '{
        "state": "The document was received by the accounting team this morning.",
        "images": ["data:image/jpeg;base64,/9j/4AAQSkZJRg..."],
        "questions": {
            "has_table": {
                "type": "noul",
                "instructions": "Does the image contain a table?"
            }
        }
    }' | jq
```

An invalid request returns the error `400`. A model that is not a decision model returns the error `501`. A request with images returns the error `501` if the model does not support image input, or if no multimodal projector is loaded.
