package account

import (
	"sync"
	"sync/atomic"
	"testing"
	"time"
)

// barrier makes the first two callers meet inside the race window. A caller
// that is alone (because the other one is correctly blocked on a lock) gives up
// after 200ms, so the test cannot hang and the outcome does not depend on
// scheduler luck.
func barrier() func() {
	var arrived atomic.Int32
	met := make(chan struct{})
	return func() {
		if arrived.Add(1) == 2 {
			close(met)
		}
		select {
		case <-met:
		case <-time.After(200 * time.Millisecond):
		}
	}
}

func TestDeterministicInterleavingDoesNotLoseADeposit(t *testing.T) {
	raceWindow = barrier()
	defer func() { raceWindow = func() {} }()

	var a Account
	var wg sync.WaitGroup
	for _, amount := range []int64{100, 50} {
		wg.Add(1)
		go func() { defer wg.Done(); a.Deposit(amount) }()
	}
	wg.Wait()

	if got := a.Balance(); got != 150 {
		t.Fatalf("balance = %d after deposits of 100 and 50, want 150 (a deposit was lost)", got)
	}
}

func TestStressManyDeposits(t *testing.T) {
	var a Account
	var wg sync.WaitGroup
	for i := 0; i < 200; i++ {
		wg.Add(1)
		go func() { defer wg.Done(); a.Deposit(1) }()
	}
	wg.Wait()
	if got := a.Balance(); got != 200 {
		t.Fatalf("balance = %d, want 200", got)
	}
}
