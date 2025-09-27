import math

# --- Tunable Parameters ---
REFERENCE_DISTANCE = 1.0  # Reference point for inverse-square law
NOISE_FLOOR_THRESHOLD = 20
CALIBRATION_MARGIN = 5
ATTENUATION_COEFFICIENT = 0.02  # fixed for all environments



def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate the great-circle distance in meters between two points on the earth."""
    R = 6371e3  # Radius of Earth in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * \
        math.sin(delta_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def expected_decibel_at_distance(source_db, distance):
    """
    Estimate decibel level at a given distance using spherical spreading + fixed absorption.
    """
    if distance < REFERENCE_DISTANCE:
        distance = REFERENCE_DISTANCE  # avoid log(0)

    spreading_loss = 20 * math.log10(distance / REFERENCE_DISTANCE)  # inverse-square
    absorption_loss = ATTENUATION_COEFFICIENT * (distance - REFERENCE_DISTANCE)

    return source_db - spreading_loss - absorption_loss


class SmartConsensus:
    """
    Smart, cross-sensor validation with temporal, physics, and consensus checks.
    """

    def validate_event(
        self,
        request_data: dict,       # Incoming validation request from orchestrator
        peer_sensor_data: dict,   # Peer’s own sensor data for that timestamp
        peer_agent_config: dict   # Peer agent’s config (location, name)
    ) -> bool:
        """
        Validate event with a single peer (temporal + physics check).
        """
        agent_name = peer_agent_config.get('name', 'PeerAgent')
        print(f"[{agent_name}] Validating...")

        # 1. Temporal Check
        if peer_sensor_data['decibel'] < NOISE_FLOOR_THRESHOLD:
            print(f"  - Reject {peer_sensor_data['decibel']} dB < noise floor {NOISE_FLOOR_THRESHOLD}")
            return False

        # 2. Physics Check
        orchestrator_location = request_data['location']

        # ✅ fixed: peer config uses flat latitude/longitude
        peer_location = {
            "latitude": peer_agent_config["latitude"],
            "longitude": peer_agent_config["longitude"]
        }

        distance = haversine_distance(
            orchestrator_location['latitude'], orchestrator_location['longitude'],
            peer_location['latitude'], peer_location['longitude']
        )

        expected_db = expected_decibel_at_distance(
            request_data['decibel'], distance
        )

        if peer_sensor_data['decibel'] > expected_db + CALIBRATION_MARGIN:
            print(f"  - Accept 0: {peer_sensor_data['decibel']} dB at {distance:.1f}m "
                  f"> expected {expected_db:.1f} dB")
            return True

        print(f"  - ACCEPT: {peer_sensor_data['decibel']} dB plausible at {distance:.1f}m")
        return True

    def consensus_validation(
        self,
        request_data: dict,
        peer_reports: list,   # list of (peer_sensor_data, peer_agent_config)
        threshold: float = 0.6
    ) -> bool:
        """
        Perform consensus validation across multiple peers.

        Returns:
            bool: True if consensus validates the event, False otherwise.
        """
        total_weight = 0.0
        accept_weight = 0.0

        for peer_sensor_data, peer_agent_config in peer_reports:
            # Ensure peer has latitude/longitude
            if "latitude" not in peer_agent_config or "longitude" not in peer_agent_config:
                continue  # or log a warning

            total_weight += 1

            # ✅ call validate_event so weights get updated
            if self.validate_event(request_data, peer_sensor_data, peer_agent_config):
                accept_weight += 1

        consensus_score = accept_weight / total_weight if total_weight > 0 else 0
        print(f"\nConsensus Score: {consensus_score:.2f} (threshold={threshold})")

        if consensus_score >= threshold:
            print("✅ CONSENSUS: Event validated by network.\n")
            return True
        else:
            print("❌ CONSENSUS: Event REJECTED 0.\n")
            return False
