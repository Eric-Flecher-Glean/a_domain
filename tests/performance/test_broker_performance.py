"""
Performance tests for ProtocolBrokerAgent.

Tests AC4: Handles 100+ messages/sec throughput
"""

import pytest
import time
import threading
from typing import List
from src.a_domain.protocol.broker import ProtocolBrokerAgent
from src.a_domain.protocol.message import ProtocolMessage, Agent, Security


class PerformanceMetrics:
    """Track performance metrics for testing."""

    def __init__(self):
        self.messages_sent = 0
        self.messages_received = 0
        self.start_time = None
        self.end_time = None
        self.lock = threading.Lock()

    def start(self):
        """Start timing."""
        self.start_time = time.time()

    def stop(self):
        """Stop timing."""
        self.end_time = time.time()

    def increment_sent(self):
        """Increment sent counter."""
        with self.lock:
            self.messages_sent += 1

    def increment_received(self):
        """Increment received counter."""
        with self.lock:
            self.messages_received += 1

    @property
    def duration(self) -> float:
        """Get duration in seconds."""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return 0.0

    @property
    def throughput(self) -> float:
        """Get throughput in messages/sec."""
        if self.duration > 0:
            return self.messages_received / self.duration
        return 0.0

    def to_dict(self):
        """Convert to dictionary."""
        return {
            "messages_sent": self.messages_sent,
            "messages_received": self.messages_received,
            "duration_seconds": self.duration,
            "throughput_msg_per_sec": self.throughput
        }


class TestBrokerPerformance:
    """Performance tests for broker throughput."""

    def test_single_agent_throughput(self):
        """Test throughput with single sender/receiver pair."""
        broker = ProtocolBrokerAgent()
        metrics = PerformanceMetrics()

        # Register receiver
        def receiver_handler(message):
            metrics.increment_received()

        broker.register_agent("receiver", receiver_handler)

        # Create message template
        source = Agent(agent_id="sender", domain="test", version="1.0.0")
        target = Agent(agent_id="receiver", domain="test", version="1.0.0")
        security = Security(auth_token="test-token")

        # Send messages
        message_count = 200
        metrics.start()

        for i in range(message_count):
            message = ProtocolMessage(
                source_agent=source,
                target_agent=target,
                message_type="request",
                intent="test",
                payload={"index": i},
                security=security
            )
            broker.route_message(message)
            metrics.increment_sent()

        metrics.stop()

        # Verify throughput
        print(f"\nSingle Agent Performance:")
        print(f"  Messages: {metrics.messages_sent}")
        print(f"  Duration: {metrics.duration:.3f}s")
        print(f"  Throughput: {metrics.throughput:.1f} msg/sec")

        assert metrics.messages_received == message_count
        assert metrics.throughput > 100  # Must exceed 100 msg/sec

    def test_concurrent_agents_throughput(self):
        """Test throughput with multiple concurrent agents."""
        broker = ProtocolBrokerAgent()
        metrics = PerformanceMetrics()

        # Register multiple receivers
        num_receivers = 5

        def create_handler(agent_id):
            def handler(message):
                metrics.increment_received()
            return handler

        for i in range(num_receivers):
            broker.register_agent(f"receiver-{i}", create_handler(f"receiver-{i}"))

        # Send messages from multiple senders to multiple receivers
        messages_per_pair = 100
        total_messages = num_receivers * messages_per_pair

        security = Security(auth_token="test-token")

        metrics.start()

        for receiver_idx in range(num_receivers):
            source = Agent(agent_id=f"sender-{receiver_idx}", domain="test", version="1.0.0")
            target = Agent(agent_id=f"receiver-{receiver_idx}", domain="test", version="1.0.0")

            for i in range(messages_per_pair):
                message = ProtocolMessage(
                    source_agent=source,
                    target_agent=target,
                    message_type="request",
                    intent="test",
                    payload={"index": i},
                    security=security
                )
                broker.route_message(message)
                metrics.increment_sent()

        metrics.stop()

        # Verify throughput
        print(f"\nConcurrent Agents Performance:")
        print(f"  Agents: {num_receivers}")
        print(f"  Messages: {metrics.messages_sent}")
        print(f"  Duration: {metrics.duration:.3f}s")
        print(f"  Throughput: {metrics.throughput:.1f} msg/sec")

        assert metrics.messages_received == total_messages
        assert metrics.throughput > 100  # Must exceed 100 msg/sec

    def test_threaded_message_sending(self):
        """Test throughput with multi-threaded message sending."""
        broker = ProtocolBrokerAgent()
        metrics = PerformanceMetrics()

        # Register receiver
        def receiver_handler(message):
            metrics.increment_received()

        broker.register_agent("receiver", receiver_handler)

        # Thread worker
        def send_messages(thread_id, count):
            source = Agent(agent_id=f"sender-{thread_id}", domain="test", version="1.0.0")
            target = Agent(agent_id="receiver", domain="test", version="1.0.0")
            security = Security(auth_token="test-token")

            for i in range(count):
                message = ProtocolMessage(
                    source_agent=source,
                    target_agent=target,
                    message_type="request",
                    intent="test",
                    payload={"thread": thread_id, "index": i},
                    security=security
                )
                broker.route_message(message)
                metrics.increment_sent()

        # Start threads
        num_threads = 4
        messages_per_thread = 100
        total_messages = num_threads * messages_per_thread

        threads = []
        metrics.start()

        for i in range(num_threads):
            thread = threading.Thread(target=send_messages, args=(i, messages_per_thread))
            threads.append(thread)
            thread.start()

        # Wait for completion
        for thread in threads:
            thread.join()

        metrics.stop()

        # Verify throughput
        print(f"\nThreaded Performance:")
        print(f"  Threads: {num_threads}")
        print(f"  Messages: {metrics.messages_sent}")
        print(f"  Duration: {metrics.duration:.3f}s")
        print(f"  Throughput: {metrics.throughput:.1f} msg/sec")

        assert metrics.messages_received == total_messages
        assert metrics.throughput > 100  # Must exceed 100 msg/sec

    def test_stress_test_1000_messages(self):
        """Stress test with 1000 messages to validate sustained throughput."""
        broker = ProtocolBrokerAgent()
        metrics = PerformanceMetrics()

        # Register multiple receivers
        num_receivers = 10
        for i in range(num_receivers):
            def create_handler():
                def handler(message):
                    metrics.increment_received()
                return handler
            broker.register_agent(f"receiver-{i}", create_handler())

        # Send 1000 messages distributed across receivers
        total_messages = 1000
        messages_per_receiver = total_messages // num_receivers

        security = Security(auth_token="test-token")

        metrics.start()

        for receiver_idx in range(num_receivers):
            source = Agent(agent_id=f"sender-{receiver_idx}", domain="test", version="1.0.0")
            target = Agent(agent_id=f"receiver-{receiver_idx}", domain="test", version="1.0.0")

            for i in range(messages_per_receiver):
                message = ProtocolMessage(
                    source_agent=source,
                    target_agent=target,
                    message_type="request",
                    intent="test",
                    payload={"index": i},
                    security=security
                )
                broker.route_message(message)
                metrics.increment_sent()

        metrics.stop()

        # Verify sustained throughput
        print(f"\nStress Test Performance:")
        print(f"  Messages: {metrics.messages_sent}")
        print(f"  Duration: {metrics.duration:.3f}s")
        print(f"  Throughput: {metrics.throughput:.1f} msg/sec")

        assert metrics.messages_received == total_messages
        assert metrics.throughput > 100  # Must sustain 100+ msg/sec

    def test_with_contract_validation(self):
        """Test throughput with contract validation overhead."""
        broker = ProtocolBrokerAgent()
        metrics = PerformanceMetrics()

        # Register agents
        def handler(message):
            metrics.increment_received()

        broker.register_agent("agent-a", handler)
        broker.register_agent("agent-b", handler)

        # Create contract
        handshake_result = broker.initiate_handshake("agent-a", "agent-b", "test")
        handshake_id = handshake_result.details["handshake_id"]
        accept_result = broker.accept_handshake(handshake_id)
        contract_id = accept_result.details["contract_id"]

        # Send messages with contract validation
        message_count = 200
        source = Agent(agent_id="agent-a", domain="test", version="1.0.0")
        target = Agent(agent_id="agent-b", domain="test", version="1.0.0")
        security = Security(auth_token="test-token")

        metrics.start()

        for i in range(message_count):
            message = ProtocolMessage(
                source_agent=source,
                target_agent=target,
                message_type="request",
                intent="test",
                payload={"contract_id": contract_id, "index": i},
                security=security
            )
            broker.route_message(message)
            metrics.increment_sent()

        metrics.stop()

        # Verify throughput even with contract validation
        print(f"\nContract Validation Performance:")
        print(f"  Messages: {metrics.messages_sent}")
        print(f"  Duration: {metrics.duration:.3f}s")
        print(f"  Throughput: {metrics.throughput:.1f} msg/sec")

        assert metrics.messages_received == message_count
        assert metrics.throughput > 100  # Must exceed 100 msg/sec even with validation

    def test_latency_p50_p99(self):
        """Test message latency percentiles."""
        broker = ProtocolBrokerAgent()
        latencies = []

        # Register receiver that tracks latency
        def receiver_handler(message):
            # Calculate latency from timestamp
            sent_time = message.payload.get("sent_time")
            if sent_time:
                latency = (time.time() - sent_time) * 1000  # Convert to ms
                latencies.append(latency)

        broker.register_agent("receiver", receiver_handler)

        # Send messages
        source = Agent(agent_id="sender", domain="test", version="1.0.0")
        target = Agent(agent_id="receiver", domain="test", version="1.0.0")
        security = Security(auth_token="test-token")

        for i in range(200):
            message = ProtocolMessage(
                source_agent=source,
                target_agent=target,
                message_type="request",
                intent="test",
                payload={"index": i, "sent_time": time.time()},
                security=security
            )
            broker.route_message(message)

        # Calculate percentiles
        latencies.sort()
        p50_idx = int(len(latencies) * 0.50)
        p99_idx = int(len(latencies) * 0.99)

        p50 = latencies[p50_idx] if p50_idx < len(latencies) else 0
        p99 = latencies[p99_idx] if p99_idx < len(latencies) else 0

        print(f"\nLatency Percentiles:")
        print(f"  P50: {p50:.2f}ms")
        print(f"  P99: {p99:.2f}ms")

        # Verify latency targets from architecture doc
        assert p50 < 100  # P50 should be < 100ms
        assert p99 < 250  # P99 should be < 250ms


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])  # -s to show print output
