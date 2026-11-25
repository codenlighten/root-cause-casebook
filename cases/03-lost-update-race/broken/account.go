// Package account holds a balance that several request handlers update.
package account

// raceWindow is called between reading and writing the balance. It does
// nothing in normal use; tests replace it to force one specific interleaving.
var raceWindow = func() {}

type Account struct {
	balance int64
}

func (a *Account) Deposit(amount int64) {
	current := a.balance
	raceWindow()
	a.balance = current + amount
}

func (a *Account) Balance() int64 {
	return a.balance
}
