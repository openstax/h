FROM gliderlabs/alpine:3.4
MAINTAINER Hypothes.is Project and contributors

# Install system build and runtime dependencies.
RUN apk-install \
    bash \
    ca-certificates \
    collectd \
    collectd-nginx \
    curl \
    libffi \
    libpq \
    make \
    nginx \
    python \
    py-pip \
    nodejs \
    git

RUN curl https://raw.githubusercontent.com/eficode/wait-for/master/wait-for -o /usr/local/bin/wait-for \
  && chmod a+x /usr/local/bin/wait-for

# Create the hypothesis user, group, home directory and package directory.
RUN addgroup -S hypothesis && adduser -S -G hypothesis -h /code hypothesis
WORKDIR /code

# Ensure nginx state and log directories writeable by unprivileged user.
RUN chown -R hypothesis:hypothesis /var/log/nginx /var/lib/nginx

# Copy minimal data to allow installation of dependencies.
COPY requirements.txt ./

# Install build deps, build, and then clean up.
RUN apk-install --virtual build-deps \
    build-base \
    libffi-dev \
    postgresql-dev \
    python-dev \
  && pip install --no-cache-dir -U pip supervisor \
  && pip install --no-cache-dir -r requirements.txt \
  && apk del build-deps

# Copy nginx config
COPY conf/nginx.conf /etc/nginx/nginx.conf

# Copy collectd config
COPY conf/collectd.conf /etc/collectd/collectd.conf
RUN mkdir /etc/collectd/collectd.conf.d \
 && chown hypothesis:hypothesis /etc/collectd/collectd.conf.d

# Copy the rest of the application files.
COPY . .

# If we're building from a git clone, ensure that .git is writeable
RUN [ -d .git ] && chown -R hypothesis:hypothesis .git || :

# Build frontend assets
RUN npm install --production \
  && NODE_ENV=production node_modules/.bin/gulp build \
  && npm cache clean

# Expose the default port.
EXPOSE 5000

# Set the application environment
ENV PATH /code/bin:$PATH
ENV PYTHONIOENCODING utf_8
ENV PYTHONPATH /code:$PYTHONPATH

# Start the web server by default
USER hypothesis

ENTRYPOINT ["/code/docker/entrypoint"]

CMD ["init-env", "supervisord", "-c" , "conf/supervisord.conf"]
