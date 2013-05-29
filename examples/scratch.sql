/* get all subreddits that have filter 1 flag set */
SELECT DISTINCT( subreddit_name )
FROM `reddit_data_subreddit_time_series_data`
WHERE filter_1 = 1
ORDER BY subreddit_name;
/* 1923 records */

SELECT COUNT( DISTINCT( subreddit_name ) )
FROM reddit_collect_post;
/* 35371 records */

/* Try collecting comments for all 1923? */

/* look at top numbers of posts */
SELECT subreddit_name, COUNT( * ) as period_count, SUM( post_count ) as post_count, SUM( num_comments_average * post_count ) as comment_count
FROM `reddit_data_subreddit_time_series_data`
WHERE filter_1 = 1
GROUP BY subreddit_name
ORDER BY post_count DESC;

/* order by number of time present in */
SELECT subreddit_name, COUNT( * ) as period_count, SUM( post_count ) as post_count, SUM( num_comments_average * post_count ) as comment_count
FROM `reddit_data_subreddit_time_series_data`
WHERE filter_1 = 1
GROUP BY subreddit_name
ORDER BY period_count DESC;

/* test updating post table to add subreddits to database. */
SELECT subreddit_id, subreddit_reddit_id
FROM `reddit_collect_post`
WHERE subreddit_reddit_id = 't5_2s78w';

UPDATE `reddit_collect_post`
SET subreddit_id = 1
WHERE subreddit_reddit_id = 't5_2s78w';

/* test updating comment table to add subreddits to database. */
SELECT *
FROM `reddit_collect_comment`
WHERE subreddit_reddit_id = 't5_2s78w';

UPDATE `reddit_collect_comment`
SET subreddit_id = 1
WHERE subreddit_reddit_id = 't5_2s78w';

/* test updating time series table to add subreddits to database. */
SELECT *
FROM `reddit_data_subreddit_time_series_data`
WHERE subreddit_reddit_id = 't5_2s78w';

UPDATE `reddit_data_subreddit_time_series_data`
SET subreddit_id = 1
WHERE subreddit_reddit_id = 't5_2s78w';

/* see if all the rows that needed to got updated. */
SELECT COUNT( * )
FROM reddit_data_subreddit_time_series_data
WHERE subreddit_id = 31;

SELECT COUNT( * )
FROM reddit_data_subreddit_time_series_data
WHERE subreddit_reddit_id = 't5_2s78w';

SELECT COUNT( * )
FROM reddit_data_subreddit_time_series_data
WHERE subreddit_reddit_id = 't5_2x3j9';

SELECT COUNT( * )
FROM reddit_data_subreddit_time_series_data
WHERE subreddit_id = 33;

SELECT COUNT( * )
FROM reddit_data_subreddit_time_series_data
WHERE subreddit_reddit_id = 't5_2vjtm';

/* counts of domains */
SELECT domain, COUNT( * ) AS use_count
FROM `reddit_collect_post`
GROUP BY domain
ORDER BY use_count DESC
LIMIT 100;

/* self-posts have domain of "self.<subreddit_name>". */
/* URL shorteners included as well */

/*=============================================================================*/
/* POSTS - filter on '%boston%'
/*=============================================================================*/

/* set filter flag on posts that contain "boston" - first, test select */
SELECT COUNT( * )
FROM `socs_reddit`.`reddit_collect_post`
WHERE
(
     ( LOWER( title ) LIKE '%boston%' )
     OR ( LOWER( title ) LIKE 'boston%' )
     OR ( LOWER( title ) LIKE '%boston' )
     OR ( LOWER( selftext ) LIKE '%boston%' )
     OR ( LOWER( selftext ) LIKE 'boston%' )
     OR ( LOWER( selftext ) LIKE '%boston' )
);

/* a little less crazy - will it work? */
SELECT COUNT( * )
FROM `socs_reddit`.`reddit_collect_post`
WHERE
(
     ( LOWER( title ) LIKE '%boston%' )
     OR ( LOWER( selftext ) LIKE '%boston%' )
);

/* Set filter_1 based on this filter */
UPDATE `socs_reddit`.`reddit_collect_post`
SET filter_1 = 1
WHERE
(
     ( LOWER( title ) LIKE '%boston%' )
     OR ( LOWER( selftext ) LIKE '%boston%' )
);

/*=============================================================================*/
/* DOMAINS - check to make sure my updates of domains haven't broken anything.
/*=============================================================================*/

/* count non-self-post domains */
SELECT COUNT( * )
FROM `reddit_collect_domain`
WHERE is_self_post = 0;

/* count domains that start with "self." */
SELECT COUNT( * )
FROM `reddit_collect_domain`
WHERE name LIKE 'self\.%';

/* make sure the is_self_post count is the same */
SELECT COUNT( * )
FROM `reddit_collect_domain`
WHERE is_self_post = 1;