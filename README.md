#### Stockup Backend Repo

This is a repo of our backend containing a tornado + motor API server, some homebrew azure deployment scripts (which should be formalized some day through a third party framework)

Our MVP is a product that makes people money

### Respository Structure

## Branch Structure
The branches follow the __va.b.c__ format, except master. __a__ is the major release. __b__ is a release branch if it's even or a devlopment branch if it's odd. __c__ is for patches and are generally used for the release branch only. e.g. v0.1 is a development branch v0.2.1 is a release branch with one patch. 

Generally a development branch of __va.b__ gets released in branch __va.(b+1)__. 

All code is commited to master and get periodically rebased onto development branches after each sprint.

## Folder structure

# algo_parsers

algo parsers parse combination of conditions

How the algorithm is stored

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
	"primary_condition": "", // primary condition that must match exactly, the other conditions can match in a timeframe
	"conditions":
	{
		"price_condition": {
			"type": "more_than|less_than",
			"price": "PRICE_OF_STOCK",
			"window": "(int)WINDOW" // timeframe in seconds where this condition must match that of the primary condition, 0 indicates time of trade
		},
		"kdj_condition": { // D pass K for sell, K pass D for buy
			"window": ""
			"n": "9", // NOT USER CHANGEABLE FOR NOW
			"m": "3",
			"m1": "3",
			"d_upper": "100",
			"d_lower": "80"
		}
	}
}

```

price indices:

0. name
1. opening today
2. closing yesterday
3. current price