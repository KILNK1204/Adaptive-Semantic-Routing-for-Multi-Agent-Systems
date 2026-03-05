"""Training data for Method 2: Performance-Weighted Routing."""

from queries import TRAINING_QUERIES


def train_performance_classifier(classifier, agent_runners: dict):
    import time
    
    print("\n" + "=" * 80)
    print("TRAINING PERFORMANCE-WEIGHTED CLASSIFIER")
    print("=" * 80)
    print(f"Training queries: {len(TRAINING_QUERIES)}")
    print()
    
    training_stats = {
        "total_queries": len(TRAINING_QUERIES),
        "successful_training": 0,
        "failed_training": 0,
        "agent_performance": {},
    }
    
    for idx, (query, expected_agent) in enumerate(TRAINING_QUERIES, 1):
        try:
            # Get the agent runner
            if expected_agent not in agent_runners:
                print(f"[{idx:2d}] [SKIP] Agent '{expected_agent}' not available")
                training_stats["failed_training"] += 1
                continue
            
            runner = agent_runners[expected_agent]
            
            # Run the query through the agent
            print(f"[{idx:2d}] Training on {expected_agent:20s} ... ", end="", flush=True)
            start_time = time.time()
            
            try:
                response, latency = runner(query)
                elapsed = time.time() - start_time
                
                # Check if agent classified it as IN_DOMAIN
                was_in_domain = response.domain == "IN_DOMAIN"
                
                # Check accuracy: did we route to the correct agent?
                # In training context, we always know the expected agent
                was_accurate = True  # We're running the expected agent, so it's always correct
                
                # Update classifier's performance statistics
                classifier.record_result(expected_agent, was_in_domain, was_accurate, latency)
                
                # Track stats
                domain_label = "[IN]" if was_in_domain else "[OUT]"
                print(f"{domain_label} ({latency:.2f}s)")
                training_stats["successful_training"] += 1
                
                # Record per-agent stats
                if expected_agent not in training_stats["agent_performance"]:
                    training_stats["agent_performance"][expected_agent] = {
                        "in_domain": 0,
                        "out_domain": 0,
                    }
                if was_in_domain:
                    training_stats["agent_performance"][expected_agent]["in_domain"] += 1
                else:
                    training_stats["agent_performance"][expected_agent]["out_domain"] += 1
                    
            except Exception as e:
                print(f"[ERROR] {str(e)[:50]}")
                training_stats["failed_training"] += 1
                
        except Exception as e:
            print(f"[{idx:2d}] [ERROR] {str(e)[:60]}")
            training_stats["failed_training"] += 1
    
    # Print training summary
    print()
    print("=" * 80)
    print("TRAINING SUMMARY")
    print("=" * 80)
    print(f"Successful training runs: {training_stats['successful_training']}/{training_stats['total_queries']}")
    print(f"Failed training runs: {training_stats['failed_training']}/{training_stats['total_queries']}")
    print()
    
    print("Agent Performance Statistics (from training):")
    for agent, perf in training_stats["agent_performance"].items():
        in_domain = perf["in_domain"]
        out_domain = perf["out_domain"]
        total = in_domain + out_domain
        in_domain_rate = (in_domain / total * 100) if total > 0 else 0
        print(f"  {agent:20s}: {in_domain:2d}/{total:2d} IN_DOMAIN ({in_domain_rate:5.1f}%)")
    
    print()
    
    # Print updated classifier statistics
    classifier_stats = classifier.get_stats()
    print("Classifier Performance Weights (after training):")
    for agent, stats in classifier_stats.items():
        accuracy_rate = stats["accuracy_rate"]
        in_domain_rate = stats["in_domain_rate"]
        combined_score = stats["combined_score"]
        avg_latency = stats["avg_latency"]
        print(f"  {agent:20s}: accuracy={accuracy_rate:.3f}, in_domain={in_domain_rate:.3f}, combined={combined_score:.3f}, latency={avg_latency:.3f}s")
    
    print("=" * 80)
    print()
    
    return training_stats
