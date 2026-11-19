# axiom/docker-erddap v2.31.1 with a patched Java runtime.
#
# CVE-2026-114938 (GHSA-6g7j-4xh3-xq2q): heap overflow in the JVM's x86-64 Base64 intrinsic, on CPUs with
# AVX-512 VBMI (all our ERDDAP hosts). The image ships Temurin 25.0.3; the fix is Temurin 25.0.5.1+2 (2026-11-18).
# Until axiom publishes an image with it, this swaps the JDK in /opt/java/openjdk (the image's JAVA_HOME).
# Drop this file and go back to `image: axiom/docker-erddap:<version>` once an upstream image ships >= 25.0.5.1.
FROM axiom/docker-erddap:v2.31.1

ARG TEMURIN_VERSION=25.0.5.1_2
ARG TEMURIN_TAG=jdk-25.0.5.1%2B2
# from Adoptium's API and the release's .sha256.txt (matched)
ARG TEMURIN_SHA256=760f91b22c3efc9bd1b64ff950598231be82928cc807e30691a0e7a2995a62c0

RUN set -eux; \
    url="https://github.com/adoptium/temurin25-binaries/releases/download/${TEMURIN_TAG}/OpenJDK25U-jdk_x64_linux_hotspot_${TEMURIN_VERSION}.tar.gz"; \
    curl -fsSL -o /tmp/jdk.tar.gz "$url"; \
    echo "${TEMURIN_SHA256}  /tmp/jdk.tar.gz" | sha256sum -c -; \
    rm -rf /opt/java/openjdk; \
    mkdir -p /opt/java/openjdk; \
    tar -xzf /tmp/jdk.tar.gz -C /opt/java/openjdk --strip-components=1 --no-same-owner; \
    rm /tmp/jdk.tar.gz; \
    java -version 2>&1 | grep -q 'Temurin-25.0.5.1+2'
