# requirements
You will implement a web scrawler in python that conducts the following workflow:
1. user enter a keyword and you search the related products on [https://www.amazon.com/](https://www.amazon.com/)
   
   ** don't need to log in
2. find the top 3 products in the search result
3. for each product, scrawl all user inputs that may contain multiple pages, return the following content:
   - content
   - star
   - time
   - commentor name
   - verified purchase
 
    the user can filter the star in the scrawl function, if so the function filters comments with the stars specified by the user (can be multiple values) and scrawl the comments.

** involves dynamic content in each page
