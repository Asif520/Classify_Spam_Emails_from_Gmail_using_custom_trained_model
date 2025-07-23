### This is a Spam classifier project. Here I trained the dataset using gridsearch() , naive_bayes, SVM & Logistic Regression models.

*  Dataset: I fetched about 300 emails directly from my gmail using python library and labelled as `spam` or   `ham`. Also combined with a public dataset of spam_message dataset from [kaggle]

*  Preoprocess: Preprocessed each email sinppet before training.
*  Trained Model: Used GridSearchCV() for hyper parameter tuning on SVM, LogisticRegression and MultinomialNB  . Saved the model and vectorizer(Tf-Idf Vectorizer).
*  #### Classify or Label: Finally fetched about 50 emails from my GMAIL and predicted using the saved vectorizer and  model.
    *  The output result is given on `output_result.txt`.
