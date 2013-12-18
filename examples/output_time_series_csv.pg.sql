/*
If postgresql command line, log in as postgres user, run psql, remember to
   connect to database ("\c socs_reddit"), and for long queries, remember to run
   inside a "screen" session (using unix command screen).
 */

/* ========================================================================== */
/* output to CSV file. */
/* ========================================================================== */

/* ==> test SELECT */
SELECT id, start_date, end_date, time_period_type, time_period_index, time_period_category, time_period_label, aggregate_index, subreddit_name, subreddit_reddit_full_id, filter_1::int AS has_boston, match_count_1 AS has_boston_count, filter_2::int AS has_news, match_count_2 AS has_news_count, post_count, self_post_count, over_18_count, COALESCE( unique_author_count, 0 ) AS unique_author_count, score_average, score_min, score_max, COALESCE( score_variance, 0 ) AS score_variance, upvotes_average, upvotes_min, upvotes_max, COALESCE( upvotes_variance, 0 ) AS upvotes_variance, downvotes_average, downvotes_min, downvotes_max, COALESCE( downvotes_variance, 0 ) AS downvotes_variance, num_comments_average, num_comments_min, num_comments_max, COALESCE( num_comments_variance, 0 ) AS num_comments_variance
FROM reddit_data_subreddit_time_series_data
ORDER BY post_count DESC
/* ORDER BY aggregate_index, subreddit_name ASC */
LIMIT 10;

/* ==> test COPY */
COPY
(
	SELECT id, start_date, end_date, time_period_type, time_period_index, time_period_category, time_period_label, aggregate_index, subreddit_name, subreddit_reddit_full_id, filter_1::int AS has_boston, match_count_1 AS has_boston_count, filter_2::int AS has_news, match_count_2 AS has_news_count, post_count, self_post_count, over_18_count, COALESCE( unique_author_count, 0 ) AS unique_author_count, score_average, score_min, score_max, COALESCE( score_variance, 0 ) AS score_variance, upvotes_average, upvotes_min, upvotes_max, COALESCE( upvotes_variance, 0 ) AS upvotes_variance, downvotes_average, downvotes_min, downvotes_max, COALESCE( downvotes_variance, 0 ) AS downvotes_variance, num_comments_average, num_comments_min, num_comments_max, COALESCE( num_comments_variance, 0 ) AS num_comments_variance
	FROM reddit_data_subreddit_time_series_data
	ORDER BY aggregate_index, subreddit_name ASC
	LIMIT 10
)
TO '<full_path_to_output_file>.csv' DELIMITER ',' CSV HEADER;

/* ==> COPY */
COPY
(
	SELECT id, start_date, end_date, time_period_type, time_period_index, time_period_category, time_period_label, aggregate_index, subreddit_name, subreddit_reddit_full_id, filter_1::int AS has_boston, match_count_1 AS has_boston_count, filter_2::int AS has_news, match_count_2 AS has_news_count, post_count, self_post_count, over_18_count, COALESCE( unique_author_count, 0 ) AS unique_author_count, score_average, score_min, score_max, COALESCE( score_variance, 0 ) AS score_variance, upvotes_average, upvotes_min, upvotes_max, COALESCE( upvotes_variance, 0 ) AS upvotes_variance, downvotes_average, downvotes_min, downvotes_max, COALESCE( downvotes_variance, 0 ) AS downvotes_variance, num_comments_average, num_comments_min, num_comments_max, COALESCE( num_comments_variance, 0 ) AS num_comments_variance
	FROM reddit_data_subreddit_time_series_data
	ORDER BY aggregate_index, subreddit_name ASC
)
TO '<full_path_to_output_file>.csv' DELIMITER ',' CSV HEADER;