/*
 * Licensed to the Apache Software Foundation (ASF) under one or more
 * contributor license agreements.  See the NOTICE file distributed with
 * this work for additional information regarding copyright ownership.
 * The ASF licenses this file to You under the Apache License, Version 2.0
 * (the "License"); you may not use this file except in compliance with
 * the License.  You may obtain a copy of the License at
 *
 *    http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package twitterapp;

import java.util.Arrays;
import java.util.Comparator;
import java.util.List;
import java.util.regex.Pattern;

import scala.Tuple2;
import twitter4j.Status;

import org.apache.log4j.Level;
import org.apache.log4j.Logger;
import org.apache.spark.SparkConf;
import org.apache.spark.api.java.function.*;
import org.apache.spark.api.java.JavaRDD;
import org.apache.spark.api.java.JavaPairRDD;
import org.apache.spark.api.java.Optional;
import org.apache.spark.api.java.StorageLevels;
import org.apache.spark.streaming.Duration;
import org.apache.spark.streaming.Durations;
import org.apache.spark.streaming.State;
import org.apache.spark.streaming.StateSpec;
import org.apache.spark.streaming.api.java.*;
import org.apache.spark.streaming.twitter.TwitterUtils;

public class Hashtags{
  private static final Pattern SPACE = Pattern.compile(" ");

  public static void main(String[] args) throws Exception {
	  
	  	Logger.getLogger("org").setLevel(Level.ERROR);
	  	Logger.getLogger("akka").setLevel(Level.ERROR);
	  	
	  	String consumerKey = "9291b929p3yPoywP9AU2rMe5q";
	    String consumerSecret = "wq31JgHL0aoWkM3gn2DQfGt1F1QkBbgHUbRugigunTjNGCQ1Nz";
	    String accessToken = "1087607633823952898-G6ThN1w8jT7MSg0aNJcWOnrxGpmhPw";
	    String accessTokenSecret = "zKUF22CzGgoMNii7bpiRyXEqdfFwS31zYjz2rFwrCBiwx";
	    String[] filters = {"coronavirus news", "breaking"}; 
	    
	    // Set the system properties so that Twitter4j library used by Twitter stream
	    // can use them to generate OAuth credentials
	    System.setProperty("twitter4j.oauth.consumerKey", consumerKey);
	    System.setProperty("twitter4j.oauth.consumerSecret", consumerSecret);
	    System.setProperty("twitter4j.oauth.accessToken", accessToken);
	    System.setProperty("twitter4j.oauth.accessTokenSecret", accessTokenSecret);

	    SparkConf sparkConf = new SparkConf().setMaster("local[*]").setAppName("TwitterApp");

	    JavaStreamingContext jssc = new JavaStreamingContext(sparkConf, Durations.seconds(60));
	    JavaReceiverInputDStream<Status> stream = TwitterUtils.createStream(jssc, filters);

        JavaDStream<String> txtTweets = stream.map(s ->s.getText().replace('\n', ' '));
        JavaDStream<String> wordsTweets = txtTweets.flatMap(x -> Arrays.asList(x.split(" ")).iterator());
        JavaDStream<String> hashtags = wordsTweets.filter(s -> s.startsWith("#"));
 
        JavaPairDStream<String, Integer> hashtagsPair = hashtags.mapToPair(s -> new Tuple2<>(s, 1));
        JavaPairDStream<String, Integer> hashtagsOcc = hashtagsPair.reduceByKey((a, b) -> a + b);
     
        JavaPairDStream<Integer, String> hashtagsOccReverse = hashtagsOcc.mapToPair(t -> new Tuple2<Integer, String>(t._2, t._1));
        JavaPairDStream<Integer, String> sortedHashtags = hashtagsOccReverse.transformToPair(rdd -> rdd.sortByKey(false));        
        
        sortedHashtags.foreachRDD( x-> {
            x.collect().stream().limit(10).forEach(n-> System.out.println(n));
        });
        jssc.start();
        jssc.awaitTermination();
  }
}
