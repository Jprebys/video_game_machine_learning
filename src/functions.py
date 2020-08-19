
def get_all_word2vec(tokens_list, vector, generate_missing=False, k=300, sent_length=100):
    imputed = 0
    if len(tokens_list)<1:
        return np.zeros(k)
    if generate_missing:
        vectorized = [vector[word] if word in vector else np.random.rand(k) for word in tokens_list]
        
    else:
        vectorized = [vector[word] if word in vector else np.zeros(k) for word in tokens_list]
    for _ in range(sent_length - len(tokens_list)):
        vectorized.append(np.zeros(k))
    return np.array(vectorized[:sent_length])




def get_word2vec_embeddings(vectors, clean_questions, generate_missing=False, k=300, sent_length=100):
    embeddings = df['tokens'].apply(lambda x: get_all_word2vec(x, vectors, generate_missing=generate_missing, k=k, sent_length=sent_length))
    return list(embeddings)



def clean_text(text):
    
    # Removes punctuation
    words = [''.join(ch for ch in s if ch not in string.punctuation)\
             for s in text.split()]
    
    # Returns the lower-case string
    return ' '.join(words).lower()


def bin_scores(score):
    if score > 60:
        if score > 75:
            return 2
        return 1
    return 0





def build_kum_cnn_graph(sent_len, word_vec, out_dim, filters = 64, n_grams = [2,3], num_dense_layers = 3):
    '''
    args:
        sent_len: length of input sentense. if raw sentense is less than it, using zero padding, else cut down to it.
        word_vec: dim of word vector embedding using pre-trained glove or word2vec model
        out_dim: dim of output y
        filters: filters for Convolutional layers
        n_grams: list of ngram for Convolutional layers kernal. each will generate one cell output. details can be referred from paper
        num_dense_layers: to decide how many dense layers after concatenating all Convolutional layers output
    returns:
        Keras Model
    '''
    inputs = keras.layers.Input(shape=(sent_len, word_vec, 1))
    merged_layer = []
    for h in n_grams:
        conv_layer = keras.layers.Conv2D(filters, (h, word_vec), activation='relu')(inputs)
        pool_layer = keras.layers.MaxPooling2D(pool_size=(sent_len-h+1, 1))(conv_layer)
        merged_layer.append(pool_layer)
    concat_layer = keras.layers.concatenate(merged_layer)
    flatten_layer = keras.layers.Flatten()(concat_layer)
    in_ = flatten_layer
    prev_units = filters * len(n_grams)
    for _ in range(num_dense_layers - 1):
        prev_units /= 2
        dense_layer = keras.layers.Dense(int(prev_units), 
                        activation='relu', 
                        kernel_regularizer = keras.regularizers.l2(0.01),
                        # activity_regularizer = keras.regularizers.l1(0)
                                        )(in_)
        drop_layer = keras.layers.Dropout(.5)(dense_layer)
        in_ = drop_layer
        
    outputs = keras.layers.Dense(out_dim, activation = 'softmax')(in_)
    
    model = keras.models.Model(inputs = inputs, outputs = outputs)
#     model.summary()
    return model