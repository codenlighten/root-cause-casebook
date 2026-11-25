//! Size accounting for chunked uploads.

/// Total size in bytes of `chunks` chunks of `chunk_size` bytes each.
pub fn total_size(chunks: u32, chunk_size: u32) -> u64 {
    (chunks * chunk_size) as u64
}

#[cfg(test)]
mod tests {
    use super::total_size;

    #[test]
    fn five_thousand_one_mib_chunks_is_about_five_gib() {
        // 5,000 * 1,048,576 = 5,242,880,000, which does not fit in a u32.
        assert_eq!(total_size(5_000, 1_048_576), 5_242_880_000);
    }

    #[test]
    fn small_uploads_are_unchanged() {
        assert_eq!(total_size(3, 1_024), 3_072);
    }

    #[test]
    fn largest_possible_inputs_do_not_overflow() {
        assert_eq!(total_size(u32::MAX, u32::MAX), (u32::MAX as u64) * (u32::MAX as u64));
    }
}
