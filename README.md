stockup-backend
===============

Backend for stockup

Our MVP is a product that makes people money

How the algorithm is stored and

```json

{
	"algo_id": "SOME_UNIQUE_ID",
	"algo_v": "VERSION" // version is updated every time a user makes a change
	"user_id": "USER_ID",
	"stock_id": "STOCK_THIS_ALGO_APPLIES_TO",
	"algo_name": "NAME_OF_ALGO",
	"price_type": "market|limited",
	"trade_method": "buy|sell",
	"volume": "NUM_STOCK_TO_TRADE",
	"conditions":
	{
		"primary_condition": "", // primary condition that must match exactly, the other conditions can match in a timeframe
		"price_condition": {
			"type": "more_than|less_than",
			"price": "PRICE_OF_STOCK",
			"window": "WINDOW" // timeframe in seconds where this condition must match that of the primary condition, 0 indicates time of trade
		},
		"kdj_condition": { // D pass K for sell, K pass D for buy
			"window": "WINDOW",
			"n": "9", // NOT USER CHANGEABLE FOR NOW
			"m": "3",
			"m1": "3",
			"d_upper": "100",
			"d_lower": "80"
		}
	}
}

```