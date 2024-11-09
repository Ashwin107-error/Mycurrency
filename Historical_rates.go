package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"io/ioutil"
	"time"
	"sync"
	_ "github.com/lib/pq"
	"github.com/go-redis/redis/v8"
	"context"
)

var (
	db          *sql.DB
	redisClient *redis.Client
	ctx         = context.Background()
)

// Structure Definitions
type Meta struct {
	Code       int    `json:"code"`
	Disclaimer string `json:"disclaimer"`
}

type CurrencyRate struct {
	Date  string             `json:"date"`
	Base  string             `json:"base"`
	Rates map[string]float64 `json:"rates"`
}

type APIResponse struct {
	Meta     Meta         `json:"meta"`
	Response CurrencyRate `json:"response"`
}

// Initialize PostgreSQL Database
func initDB() {
	connStr := "user=ashwin password=routemobile dbname=ashwin sslmode=disable"
	var err error
	db, err = sql.Open("postgres", connStr)
	if err != nil || db.Ping() != nil {
		log.Fatalf("Error connecting to database: %v", err)
	}
	log.Println("Database connection established.")
}

// Initialize Redis client
func initRedis() {
	redisClient = redis.NewClient(&redis.Options{
		Addr: "localhost:6379",
	})
	if _, err := redisClient.Ping(ctx).Result(); err != nil {
		log.Fatalf("Could not connect to Redis: %v", err)
	}
	log.Println("Redis connection established.")
}

// Retrieve the last processed date from Redis
func getLastProcessedDate() time.Time {
	dateStr, err := redisClient.Get(ctx, "last_processed_date").Result()
	if err != nil {
		// Default start date
		return time.Date(1997, 10, 14, 0, 0, 0, 0, time.UTC)
	}

	date, err := time.Parse("2006-01-02", dateStr)
	if err != nil {
		return time.Date(1997, 10, 14, 0, 0, 0, 0, time.UTC)
	}
	return date
}

// Update the last processed date in Redis
func setLastProcessedDate(date string) {
	redisClient.Set(ctx, "last_processed_date", date, 0)
}

// Main data fetching function
func fetchHistoricalRates(date time.Time, baseCurrency string, ch chan<- APIResponse, wg *sync.WaitGroup) {
	defer wg.Done()
	dateStr := date.Format("2006-01-02")
	log.Printf("Fetching rates for date: %s", dateStr)
	url := fmt.Sprintf("https://api.currencybeacon.com/v1/historical?api_key=z7vnFV1FLhChDhOuVeXg80AoQtNTWc6i&date=%s&base=%s", dateStr, baseCurrency)

	resp, err := http.Get(url)
	if err != nil {
		log.Printf("Error fetching data for date %s: %v", dateStr, err)
		return
	}
	defer resp.Body.Close()

	body, err := ioutil.ReadAll(resp.Body)
	if err != nil || resp.StatusCode != 200 {
		log.Printf("Error reading response for date %s: %v", dateStr, err)
		return
	}

	var apiResponse APIResponse
	if err = json.Unmarshal(body, &apiResponse); err != nil || len(apiResponse.Response.Rates) == 0 {
		log.Printf("No rates available for date %s with base currency %s. Skipping...", dateStr, baseCurrency)
		return
	}

	log.Printf("Successfully fetched data for date %s with base currency %s", dateStr, apiResponse.Response.Base)
	ch <- apiResponse
}

// Store the response data in the database
func storeInDatabase(apiResponse APIResponse) {
	log.Printf("Storing rates for date: %s", apiResponse.Response.Date)

	tx, err := db.Begin()
	if err != nil {
		log.Printf("Failed to begin transaction: %v", err)
		return
	}

	stmt, err := tx.Prepare(`
		INSERT INTO currencyrate (date, base_currency, currency_code, rate)
		VALUES ($1, $2, $3, $4)
		ON CONFLICT (date, currency_code) DO NOTHING
	`)
	if err != nil {
		tx.Rollback()
		log.Printf("Failed to prepare statement: %v", err)
		return
	}
	defer stmt.Close()

	for currency, rateValue := range apiResponse.Response.Rates {
		_, err := stmt.Exec(apiResponse.Response.Date, apiResponse.Response.Base, currency, rateValue)
		if err != nil {
			tx.Rollback()
			log.Printf("Failed to insert rate for date %s and currency %s: %v", apiResponse.Response.Date, currency, err)
			return
		}
	}

	if err = tx.Commit(); err != nil {
		log.Printf("Failed to commit transaction: %v", err)
		return
	}

	// Update Redis with the last processed date
	setLastProcessedDate(apiResponse.Response.Date)
}

func main() {
	initDB()
	initRedis()
	defer db.Close()

	baseCurrency := "USD"
	ch := make(chan APIResponse)
	var wg sync.WaitGroup

	// Start date from Redis or default
	currentDate := getLastProcessedDate()

	// Start a goroutine to store data in the database
	go func() {
		for response := range ch {
			storeInDatabase(response)
		}
	}()

	// Infinite loop to continuously fetch rates with rate limiting
	for {
		wg.Add(1)
		go fetchHistoricalRates(currentDate, baseCurrency, ch, &wg)
		currentDate = currentDate.AddDate(0, 0, 1) // Move to the next date

		// Sleep to respect rate limits (adjust sleep duration if needed)
		time.Sleep(2 * time.Second) // This delays each request to avoid overwhelming the API
	}

	wg.Wait()
	close(ch) // Close channel after all fetches are done
	log.Println("Completed processing rates.")
}
