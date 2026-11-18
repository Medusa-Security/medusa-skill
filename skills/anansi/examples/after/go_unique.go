package main

func uniqueInOrder(values []string) []string {
	seen := make(map[string]struct{}, len(values))
	result := make([]string, 0, len(values))
	for _, value := range values {
		if _, ok := seen[value]; ok {
			continue
		}
		// Append on first sighting so the result keeps input order instead of map iteration order.
		seen[value] = struct{}{}
		result = append(result, value)
	}
	return result
}
