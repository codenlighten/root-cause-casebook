// Package account holds a balance that several request handlers update.
package account

import "sync"

// raceWindow is called between reading and writing the balance. It does
// nothing in normal use; tests replace it to force one specific interleaving.
var raceWindow = func() {}

type Account struct {
	mu      sync.Mutex
	balance int64
}

// Deposit holds the lock across the whole read-modify-write. Locking the read
// and the write separately would silence the race detector and still lose updates.
func (a *Account) Deposit(amount int64) {
	a.mu.Lock()
	defer a.mu.Unlock()
	current := a.balance
	raceWindow()
	a.balance = current + amount
}

func (a *Account) Balance() int64 {
	a.mu.Lock()
	defer a.mu.Unlock()
	return a.balance
}
